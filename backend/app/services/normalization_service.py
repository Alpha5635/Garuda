import re
from typing import Any
from rapidfuzz import process, fuzz
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
                        num_val = num_val * 1000 # convert to grams for uniform comparison
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
            elif field_name == "month_year":
                match = re.search(r'(\d{2})[/\.-](\d{2,4})', raw_val)
                if match:
                    m = int(match.group(1))
                    y = int(match.group(2))
                    if y < 100:
                        y += 2000
                    norm_val = f"{y:04d}-{m:02d}"

            # 4. Manufacturer & Address RapidFuzz fuzzy match
            elif field_name == "manufacturer":
                # Clean company suffix
                norm_val = re.sub(r'\s+', ' ', raw_val).strip()

            # Find matching bounding box
            bbox = None
            for item in ocr_items:
                if candidate.raw_snippet and candidate.raw_snippet in item.raw_text:
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
