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
                match = re.search(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|ltr|gm|grams)', raw_val, re.IGNORECASE)
                if match:
                    num_val = float(match.group(1))
                    raw_unit = match.group(2).lower()
                    if raw_unit in ["g", "gm", "grams"]:
                        unit = "g"
                    elif raw_unit in ["kg"]:
                        unit = "kg"
                    elif raw_unit in ["ml"]:
                        unit = "ml"
                    elif raw_unit in ["l", "ltr"]:
                        unit = "L"
                    norm_val = f"{num_val} {unit}"

            # 3. Unit Sale Price (USP)
            elif field_name == "unit_sale_price":
                match = re.search(r'(\d+(?:\.\d{1,2})?)\s*/\s*([a-zA-Z]+)', raw_val)
                if match:
                    num_val = float(match.group(1))
                    unit = match.group(2)
                    norm_val = f"₹ {num_val:.2f}/{unit}"

            # 4. Dates (Mfg / Expiry / Best Before)
            elif field_name in ["manufacturing_date", "expiry_date", "best_before"]:
                # Match DD/MM/YYYY or MM/YYYY
                match = re.search(r'(\d{1,2})[/.-](\d{1,2}|[a-zA-Z]{3,9})[/.-](\d{2,4})', raw_val)
                if match:
                    norm_val = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"

            # 5. Manufacturer / Country of Origin
            elif field_name in ["manufacturer_name", "country_of_origin", "consumer_care"]:
                norm_val = raw_val.strip()

            normalized_list.append(
                NormalizedFieldSchema(
                    field_name=field_name,
                    raw_value=raw_val,
                    normalized_value=norm_val,
                    numeric_value=num_val,
                    unit=unit,
                    confidence=candidate.confidence
                )
            )

        return normalized_list


normalization_service = NormalizationService()
