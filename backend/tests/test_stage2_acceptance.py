import cv2
import numpy as np
import pytest
from httpx import AsyncClient
from app.schemas.ocr import OcrItemSchema, ExtractedFieldCandidate
from app.services.normalization_service import normalization_service
from app.services.cv.calibration_service import calibration_service, CalibrationRequest
from app.services.rules.rule_engine_service import rule_engine_service
from app.services.evidence_service import evidence_service


@pytest.mark.asyncio
async def test_stage2_end_to_end_acceptance_flow(async_client: AsyncClient, auth_headers: dict):
    """
    Acceptance Test Scenario:
    500 g package sample -> OCR extraction -> Field Normalization -> ArUco Calibration (5 px/mm)
    -> Numeral Height measured at 1.0 mm (Required: 2.0 mm for 500 g) -> Rule 7 violation generated
    -> Evidence crop stored -> Officer submits review/correction.
    """
    # 1. Simulate OCR outputs for a 500g package with small 1.0 mm numeral (5 px height at 5 px/mm scale)
    ocr_items = [
        OcrItemSchema(raw_text="GlowSoft Nourishing Lotion", confidence=0.98, bbox=[[10, 10], [300, 10], [300, 30], [10, 30]]),
        OcrItemSchema(raw_text="GlowSoft Pvt Ltd 101 Marine Drive Mumbai", confidence=0.95, bbox=[[10, 40], [400, 40], [400, 60], [10, 60]]),
        OcrItemSchema(raw_text="Net Wt. 500 g", confidence=0.96, bbox=[[10, 70], [100, 70], [100, 75], [10, 75]]), # height = 5 px
        OcrItemSchema(raw_text="MRP Rs. 250 (Incl. of all taxes)", confidence=0.94, bbox=[[10, 80], [250, 80], [250, 100], [10, 100]]),
        OcrItemSchema(raw_text="Mfg Date: 05/2026", confidence=0.92, bbox=[[10, 110], [150, 110], [150, 130], [10, 130]]),
        OcrItemSchema(raw_text="Consumer Care: 1800-111-222", confidence=0.93, bbox=[[10, 140], [300, 140], [300, 160], [10, 160]])
    ]

    # 2. Extract Raw Candidate Fields
    raw_candidates = [
        ExtractedFieldCandidate(field_name="manufacturer", value="GlowSoft Pvt Ltd 101 Marine Drive Mumbai", confidence=0.95),
        ExtractedFieldCandidate(field_name="net_quantity", value="Net Wt. 500 g", confidence=0.96, raw_snippet="Net Wt. 500 g"),
        ExtractedFieldCandidate(field_name="mrp", value="MRP Rs. 250 (Incl. of all taxes)", confidence=0.94, raw_snippet="MRP Rs. 250 (Incl. of all taxes)"),
        ExtractedFieldCandidate(field_name="month_year", value="Mfg Date: 05/2026", confidence=0.92, raw_snippet="Mfg Date: 05/2026"),
        ExtractedFieldCandidate(field_name="consumer_care", value="Consumer Care: 1800-111-222", confidence=0.93, raw_snippet="Consumer Care: 1800-111-222"),
    ]

    # 3. Field Normalization
    norm_fields = normalization_service.normalize_fields(raw_candidates, ocr_items)
    norm_qty = next(f for f in norm_fields if f.field_name == "net_quantity")

    assert norm_qty.numeric_value == 500.0
    assert norm_qty.unit == "g"

    # 4. Calibration (50 mm ArUco target = 250 px -> 5.0 px/mm scale)
    calib_req = CalibrationRequest(
        calibration_type="aruco_50mm",
        reference_width_mm=50.0,
        reference_width_px=250.0
    )
    calib_res = calibration_service.calibrate_image(b"mock_bytes", calib_req)
    assert calib_res.is_valid is True
    assert calib_res.pixels_per_mm == 5.0

    # 5. Measure Numeral Height (5 px height / 5 px/mm = 1.0 mm)
    numeral_height_mm = calibration_service.measure_numeral_height_mm(norm_qty.bounding_box, calib_res.pixels_per_mm)
    assert numeral_height_mm == 1.0

    # 6. Evaluate LMPC Rule Engine
    rule_results = rule_engine_service.evaluate_all_rules(norm_fields, calib_res)
    rule7_res = next(r for r in rule_results if r.rule_id == "LM-7-2-01")

    assert rule7_res.result == "violation"
    assert rule7_res.clause == "Rule 7(2) Table I & II"
    assert rule7_res.rule_version == "LMPC-2011/v1.0.0"
    assert "below mandatory minimum height of 2.0 mm" in rule7_res.explanation

    # 7. Generate Non-Destructive Evidence Crop
    dummy_img = np.zeros((400, 400, 3), dtype=np.uint8)
    _, img_bytes = cv2.imencode(".jpg", dummy_img)
    crop_key = evidence_service.crop_and_store_evidence(
        original_image_bytes=img_bytes.tobytes(),
        inspection_id=norm_qty.bounding_box,
        rule_id="LM-7-2-01",
        bbox=norm_qty.bounding_box
    )
    assert crop_key.startswith("evidence/inspections/")

    # 8. API Verification: Officer submits OCR correction & review
    insp_resp = await async_client.post("/api/v1/inspections", json={"product_name": "Lotion 500g"}, headers=auth_headers)
    insp_id = insp_resp.json()["id"]

    rev_resp = await async_client.post(
        f"/api/v1/reviews/inspections/{insp_id}/ocr-correction",
        json={
            "field_name": "net_quantity",
            "original_ocr_value": "Net Wt. 500 g",
            "corrected_value": "Net Quantity 500 g",
            "reason": "Officer verified package text"
        },
        headers=auth_headers
    )
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "success"
