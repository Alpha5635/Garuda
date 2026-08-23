import io
import uuid
import pytest
from httpx import AsyncClient
from app.services.cv.product_detection_service import product_detection_service
from tests.test_stage4a_batch import generate_shelf_image_bytes


@pytest.mark.asyncio
async def test_stage4b_full_end_to_end_acceptance_flow(async_client: AsyncClient, auth_headers: dict):
    """
    STAGE 4B ACCEPTANCE TEST
    Complete workflow:
    1. Inspector creates Inspection Session at physical store location.
    2. Uploads shelf display image containing multiple commodities.
    3. Product Detector discovers commodities and generates crops.
    4. Pipeline runs QC, OCR, Normalization, Calibration, Rules, Evidence, PDP Geometry, Compliance Score.
    5. Deterministic Risk Prioritization classifies products into HIGH / MEDIUM / LOW.
    6. Smart Recapture API lists products requiring attention (e.g. glare/blur/unusable).
    7. Inspector uploads non-destructive replacement crop for problematic product only.
    8. Single-product re-processing pipeline executes on new evidence.
    9. Officer conducts Human Review (recording OCR field correction).
    10. Audit Chain records cryptographic SHA-256 event trail.
    11. Official Session-level PDF Report generated and verified.
    """
    # 1. Create Inspection Session
    session_payload = {
        "location": "D-Mart Hypermarket, Andheri East, Mumbai",
        "latitude": 19.1136,
        "longitude": 72.8697,
        "gps_accuracy": 2.5,
        "client_session_id": "DMART-ANDHERI-SESS-01",
        "idempotency_key": f"stage4b-e2e-{uuid.uuid4()}"
    }
    create_res = await async_client.post("/api/v1/inspection-sessions", json=session_payload, headers=auth_headers)
    assert create_res.status_code == 201
    session_data = create_res.json()
    session_id = session_data["id"]
    assert session_data["status"] == "queued"

    # 2. Upload Shelf Image with 4 commodities
    shelf_image_bytes = generate_shelf_image_bytes(num_products=4, width=1280, height=720)
    upload_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/images/direct-upload",
        files={"file": ("dmart_shelf_display.jpg", shelf_image_bytes, "image/jpeg")},
        data={"gps_latitude": 19.1136, "gps_longitude": 72.8697},
        headers=auth_headers
    )
    assert upload_res.status_code == 200

    # 3. Check Session Summary & Live Priority Breakdown
    status_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}", headers=auth_headers)
    assert status_res.status_code == 200
    summary = status_res.json()
    assert summary["total_images"] == 1
    assert summary["total_products"] >= 3
    assert summary["processed_products"] == summary["total_products"]
    assert summary["status"] in ("complete", "partial_failure")
    assert (summary["high_priority"] + summary["medium_priority"] + summary["low_priority"]) >= 3

    # 4. Check Product Priority Triage
    prod_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/products", headers=auth_headers)
    assert prod_res.status_code == 200
    prods = prod_res.json()["products"]
    assert len(prods) >= 3

    first_prod = prods[0]
    assert first_prod["priority"] in ("high", "medium", "low")
    assert first_prod["priority_reason"] is not None
    assert first_prod["crop_reference"].startswith(f"sessions/{session_id}/crops/")

    # 5. Smart Recapture API
    recap_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/recapture", headers=auth_headers)
    assert recap_res.status_code == 200

    # 6. Single-Product Recapture Upload (Non-Destructive Replacement)
    replacement_crop_bytes = generate_shelf_image_bytes(num_products=1, width=500, height=500)
    recap_upload_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/products/{first_prod['product_id']}/recapture",
        files={"file": ("replacement_crop.jpg", replacement_crop_bytes, "image/jpeg")},
        headers=auth_headers
    )
    assert recap_upload_res.status_code == 200
    recap_upload_data = recap_upload_res.json()
    assert recap_upload_data["product_id"] == first_prod["product_id"]

    # 7. Officer Human Review on Individual Inspection (OCR correction)
    insp_id = first_prod["inspection_id"]
    insp_res = await async_client.get(f"/api/v1/inspections/{insp_id}", headers=auth_headers)
    assert insp_res.status_code == 200

    correction_payload = {
        "field_name": "net_quantity",
        "original_ocr_value": "400 g",
        "corrected_value": "400 g (Verified Net Wt.)",
        "reason": "Officer verified package weight on physical inspection"
    }
    review_res = await async_client.post(
        f"/api/v1/reviews/inspections/{insp_id}/ocr-correction",
        json=correction_payload,
        headers=auth_headers
    )
    assert review_res.status_code == 200

    # 8. Cryptographic Audit Chain Verification
    audit_res = await async_client.get(f"/api/v1/audit/verify/{insp_id}", headers=auth_headers)
    assert audit_res.status_code == 200
    audit_chain_data = audit_res.json()
    assert audit_chain_data["intact"] is True
    assert audit_chain_data["total_events"] >= 1

    # 9. Session PDF Report Generation & Verification
    report_gen_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/reports",
        json={"format": "pdf"},
        headers=auth_headers
    )
    assert report_gen_res.status_code == 200
    report_meta = report_gen_res.json()
    assert report_meta["format"] == "pdf"
    assert report_meta["file_size"] > 0
    assert len(report_meta["sha256_hash"]) == 64

    # Download report
    dl_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/reports/{report_meta['id']}/download", headers=auth_headers)
    assert dl_res.status_code == 200
    assert len(dl_res.content) == report_meta["file_size"]
    assert dl_res.headers["content-type"] == "application/pdf"
