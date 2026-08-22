import pytest
from app.schemas.ocr import ExtractedFieldCandidate, OcrItemSchema
from app.services.normalization_service import NormalizationService


def test_field_normalization():
    service = NormalizationService()

    candidates = [
        ExtractedFieldCandidate(field_name="mrp", value="MRP Rs. 249.50", confidence=0.95),
        ExtractedFieldCandidate(field_name="net_quantity", value="Net Wt. 500 g", confidence=0.96),
        ExtractedFieldCandidate(field_name="month_year", value="Mfg Date: 05/2026", confidence=0.92),
        ExtractedFieldCandidate(field_name="manufacturer", value="GlowSoft Skincare Pvt. Ltd.", confidence=0.98),
    ]

    ocr_items = [
        OcrItemSchema(raw_text="MRP Rs. 249.50", confidence=0.95, bbox=[[10, 10], [100, 10], [100, 30], [10, 30]]),
        OcrItemSchema(raw_text="Net Wt. 500 g", confidence=0.96, bbox=[[10, 40], [100, 40], [100, 60], [10, 60]]),
    ]

    norm_fields = service.normalize_fields(candidates, ocr_items)
    norm_map = {f.field_name: f for f in norm_fields}

    assert norm_map["mrp"].numeric_value == 249.50
    assert norm_map["mrp"].unit == "INR"
    assert norm_map["net_quantity"].numeric_value == 500.0
    assert norm_map["net_quantity"].unit == "g"
    assert norm_map["month_year"].normalized_value == "2026-05"
    assert "GlowSoft" in norm_map["manufacturer"].normalized_value
