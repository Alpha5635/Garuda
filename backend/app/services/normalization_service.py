import re
from typing import Any

try:
    from rapidfuzz import process, fuzz
except ImportError:
    import difflib
    class _Fuzz:
        @staticmethod
        def ratio(s1, s2):
            return int(difflib.SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio() * 100)
    class _Process:
        @staticmethod
        def extractOne(query, choices):
            matches = difflib.get_close_matches(str(query), list(choices), n=1, cutoff=0.0)
            if matches:
                best = matches[0]
                score = int(difflib.SequenceMatcher(None, str(query).lower(), best.lower()).ratio() * 100)
                idx = list(choices).index(best)
                return (best, score, idx)
            return (list(choices)[0] if choices else "", 0, 0)
    fuzz = _Fuzz()
    process = _Process()

from app.schemas.ocr import OcrItemSchema, ExtractedFieldCandidate
from app.schemas.normalization import NormalizedFieldSchema


class NormalizationService:
    def normalize_fields(
        self,
        extracted_candidates: list[ExtractedFieldCandidate],
        ocr_items: list[OcrItemSchema]
    ) -> list[NormalizedFieldSchema]:
        normalized_list: list[NormalizedFieldSchema] = []
        combined_text = "\n".join(item.raw_text for item in ocr_items)

        for candidate in extracted_candidates:
            field_name = candidate.field_name
            raw_val = candidate.value
            norm_val = raw_val
            num_val = None
            unit = None

            # 1. MRP Normalization
            if field_name == "mrp":
                match = re.search(r'(\d+(?:\.\d{1,2})?)', raw_val)
                if match:
                    num_val = float(match.group(1))
                    unit = "INR"
                    norm_val = f"₹ {num_val:.2f}"

            # 2. Net Quantity Normalization
            elif field_name == "net_quantity":
                match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)', raw_val)
                if match:
                    num_val = float(match.group(1))
                    raw_unit = match.group(2).lower()
                    # Standardize unit
                    if raw_unit in ["g", "gm", "gms", "gram", "grams"]:
                        unit = "g"
                    elif raw_unit in ["kg", "kgs", "kilogram"]:
                        unit = "kg"
                    elif raw_unit in ["ml", "mls", "millilitre"]:
                        unit = "ml"
                    elif raw_unit in ["l", "ltr", "liter", "litre"]:
                        unit = "l"
                    elif raw_unit in ["n", "unit", "units", "pc", "pcs"]:
                        unit = "N"
                    else:
                        unit = raw_unit
                    norm_val = f"{num_val} {unit}"

            # 3. Month & Year Normalization
            elif field_name in ["month_year", "manufacturing_date", "expiry_date", "best_before"]:
                match = re.search(r'(\d{2})[/\.-](\d{2,4})', raw_val)
                if match:
                    m = int(match.group(1))
                    y = int(match.group(2))
                    if y < 100:
                        y += 2000
                    norm_val = f"{y:04d}-{m:02d}"

            # 4. Manufacturer & Address RapidFuzz fuzzy match
            elif field_name in ["manufacturer", "manufacturer_name", "country_of_origin", "consumer_care"]:
                norm_val = re.sub(r'\s+', ' ', raw_val).strip()

            # Find matching bounding box
            bbox = None
            for item in ocr_items:
                if candidate.raw_snippet and candidate.raw_snippet in item.raw_text:
                    bbox = item.bbox
                    break
                elif raw_val in item.raw_text:
                    bbox = item.bbox
                    break

            normalized_list.append(
                NormalizedFieldSchema(
                    field_name=field_name,
                    raw_value=raw_val,
                    normalized_value=norm_val,
                    numeric_value=num_val,
                    unit=unit,
                    confidence=candidate.confidence,
                    bounding_box=bbox
                )
            )

        return normalized_list


normalization_service = NormalizationService()
