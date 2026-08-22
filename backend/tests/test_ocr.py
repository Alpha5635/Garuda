import pytest
from app.schemas.ocr import OcrItemSchema
from app.services.ocr.ocr_service import OcrService


def test_field_extraction_rules():
    ocr_service = OcrService()

    sample_items = [
        OcrItemSchema(
            raw_text="Manufactured By: GlowSoft Skincare Pvt. Ltd.",
            confidence=0.98,
            bbox=[[10, 10], [200, 10], [200, 30], [10, 30]],
            language="en"
        ),
        OcrItemSchema(
            raw_text="Regd Office: 101 Marine Drive, Mumbai 400021",
            confidence=0.95,
            bbox=[[10, 40], [300, 40], [300, 60], [10, 60]],
            language="en"
        ),
        OcrItemSchema(
            raw_text="GlowSoft Body Lotion",
            confidence=0.97,
            bbox=[[10, 70], [250, 70], [250, 90], [10, 90]],
            language="en"
        ),
        OcrItemSchema(
            raw_text="Net Qty: 400 g",
            confidence=0.96,
            bbox=[[10, 100], [120, 100], [120, 120], [10, 120]],
            language="en"
        ),
        OcrItemSchema(
            raw_text="MRP Rs. 249.00 (Incl. of all taxes)",
            confidence=0.94,
            bbox=[[10, 130], [280, 130], [280, 150], [10, 150]],
            language="en"
        ),
        OcrItemSchema(
            raw_text="Mfg Date: 05/2026",
            confidence=0.92,
            bbox=[[10, 160], [150, 160], [150, 180], [10, 180]],
            language="en"
        ),
        OcrItemSchema(
            raw_text="Consumer Care: 1800-111-222, support@glowsoft.example",
            confidence=0.93,
            bbox=[[10, 190], [350, 190], [350, 210], [10, 210]],
            language="en"
        ),
        OcrItemSchema(
            raw_text="Country of Origin: India",
            confidence=0.99,
            bbox=[[10, 220], [180, 220], [180, 240], [10, 240]],
            language="en"
        ),
    ]

    candidates = ocr_service.extract_fields(sample_items)
    extracted_map = {c.field_name: c.value for c in candidates}

    assert "manufacturer" in extracted_map
    assert "GlowSoft Skincare Pvt. Ltd." in extracted_map["manufacturer"]
    assert "address" in extracted_map
    assert "400021" in extracted_map["address"]
    assert "product_name" in extracted_map
    assert "lotion" in extracted_map["product_name"].lower()
    assert "net_quantity" in extracted_map
    assert "400 g" in extracted_map["net_quantity"]
    assert "mrp" in extracted_map
    assert "249.00" in extracted_map["mrp"]
    assert "month_year" in extracted_map
    assert "05/2026" in extracted_map["month_year"]
    assert "consumer_care" in extracted_map
    assert "1800-111-222" in extracted_map["consumer_care"]
    assert "country_of_origin" in extracted_map
    assert "India" in extracted_map["country_of_origin"]
