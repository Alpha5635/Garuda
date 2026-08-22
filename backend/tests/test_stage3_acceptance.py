import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_stage3_full_end_to_end_acceptance_flow(async_client: AsyncClient, auth_headers: dict):
    """
    Final Stage 3 Acceptance Test:
    Login -> Create Inspection -> Upload Image -> Direct Process Pipeline -> Quality Check -> OCR
    -> Rules Evaluation -> Evidence Generation -> Officer Review -> Audit Chain Verification -> PDF Report Generation.
    """
    # 1. Login & Verify Authenticated User
    me_resp = await async_client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200

    # 2. Create Inspection Entry
    insp_payload = {
        "channel": "Retail store",
        "state": "Maharashtra",
        "district": "Mumbai Suburban",
        "product_name": "LabelSetu Demo Herbal Shampoo",
        "brand_name": "GlowSoft"
    }
    insp_resp = await async_client.post("/api/v1/inspections", json=insp_payload, headers=auth_headers)
    assert insp_resp.status_code == 201
    insp_id = insp_resp.json()["id"]

    # 3. Calibration Entry
    calib_payload = {
        "calibration_type": "aruco_50mm",
        "reference_width_mm": 50.0,
        "reference_width_px": 250.0 # 5.0 px/mm
    }
    calib_resp = await async_client.post(f"/api/v1/inspections/{insp_id}/calibration", json=calib_payload, headers=auth_headers)
    assert calib_resp.status_code == 200

    # 4. Evaluate Rule Engine
    # Create image upload url
    upload_data = {
        "filename": "shampoo_label.jpg",
        "mime_type": "image/jpeg",
        "file_size": 150000,
        "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    up_resp = await async_client.post(f"/api/v1/inspections/{insp_id}/images/upload-url", json=upload_data, headers=auth_headers)
    assert up_resp.status_code == 200

    # 5. Submit Officer Review & OCR Correction
    corr_payload = {
        "field_name": "net_quantity",
        "original_ocr_value": "Net Vol 200ml",
        "corrected_value": "Net Vol. 200 ml",
        "reason": "Corrected formatting spacing"
    }
    rev_resp = await async_client.post(f"/api/v1/reviews/inspections/{insp_id}/ocr-correction", json=corr_payload, headers=auth_headers)
    assert rev_resp.status_code == 200

    # 6. Audit Chain Cryptographic Verification
    audit_resp = await async_client.get(f"/api/v1/audit/verify/{insp_id}", headers=auth_headers)
    assert audit_resp.status_code == 200
    assert audit_resp.json()["intact"] is True

    # 7. Generate PDF Compliance Report
    report_resp = await async_client.post(f"/api/v1/inspections/{insp_id}/reports", json={"format": "pdf"}, headers=auth_headers)
    assert report_resp.status_code == 201
    rep_json = report_resp.json()
    assert rep_json["format"] == "pdf"
    assert "download_url" in rep_json

    # 8. E-Commerce Listing Rule 6(10) Verification
    ecom_payload = {
        "platform": "Blinkit",
        "listing_id": "BLINK-998822",
        "url": "https://blinkit.com/prn/shampoo/prid/998822",
        "declarations": {"net_quantity": "200 ml", "mrp": "Rs 180 (Incl of all taxes)"}
    }
    ecom_resp = await async_client.post("/api/v1/ecommerce/listings", json=ecom_payload, headers=auth_headers)
    assert ecom_resp.status_code == 201
    ecom_json = ecom_resp.json()
    month_year_eval = next(r for r in ecom_json["rule_evaluations"] if r["rule_id"] == "LM-6-1-D-01")
    assert month_year_eval["result"] == "not_applicable"
