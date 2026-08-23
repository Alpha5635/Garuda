import uuid
import pytest
from httpx import AsyncClient
from app.services.cv.product_detection_service import product_detection_service
from tests.test_stage4a_batch import generate_shelf_image_bytes


@pytest.mark.asyncio
async def test_stage4a_full_end_to_end_acceptance_flow(async_client: AsyncClient, auth_headers: dict):
    """
    STAGE 4A ACCEPTANCE TEST
    Workflow:
    1. Officer creates Inspection Session at physical store location.
    2. Uploads retail shelf image with multiple commodities.
    3. Product Detector discovers 4 distinct products on shelf.
    4. Non-destructive evidence crops generated for each product.
    5. Individual Inspections created and queued into ProcessingJobs.
    6. QC / OCR / Normalization / Calibration / Rules / PDP evaluation executed.
    7. Overall Session Status aggregates all individual product outcomes.
    8. Products API lists bounding boxes, crops, inspection link, and status.
    """
    # 1. Create Inspection Session
    session_payload = {
        "location": "Reliance Fresh Supermarket, Connaught Place, New Delhi",
        "latitude": 28.6315,
        "longitude": 77.2167,
        "gps_accuracy": 3.5,
        "client_session_id": "RELIANCE-CP-SESS-01",
        "idempotency_key": f"acc-session-{uuid.uuid4()}"
    }
    create_res = await async_client.post("/api/v1/inspection-sessions", json=session_payload, headers=auth_headers)
    assert create_res.status_code == 201
    session_data = create_res.json()
    session_id = session_data["id"]
    assert session_data["status"] == "queued"
    assert session_data["location"] == session_payload["location"]

    # 2. Upload shelf display image with 4 distinct packaged commodities
    shelf_image_bytes = generate_shelf_image_bytes(num_products=4, width=1280, height=720)
    upload_res = await async_client.post(
        f"/api/v1/inspection-sessions/{session_id}/images/direct-upload",
        files={"file": ("supermarket_shelf.jpg", shelf_image_bytes, "image/jpeg")},
        data={"gps_latitude": 28.6315, "gps_longitude": 77.2167},
        headers=auth_headers
    )
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["status"] == "detecting_products"

    # 3. Verify Product Detection Output
    detections = product_detection_service.detect_products(shelf_image_bytes)
    assert len(detections) >= 3, f"Expected at least 3 commodities detected on shelf, got {len(detections)}"

    # 4. Verify Session Status & Progress
    status_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}", headers=auth_headers)
    assert status_res.status_code == 200
    sess_status = status_res.json()
    assert sess_status["total_images"] == 1
    assert sess_status["total_products"] >= 3
    assert sess_status["processed_products"] == sess_status["total_products"]
    assert sess_status["status"] in ("complete", "partial_failure")

    # 5. Verify Products List API
    prod_res = await async_client.get(f"/api/v1/inspection-sessions/{session_id}/products", headers=auth_headers)
    assert prod_res.status_code == 200
    prod_list = prod_res.json()
    assert prod_list["total_products"] >= 3
    assert len(prod_list["products"]) >= 3

    for item in prod_list["products"]:
        assert item["detection_id"] is not None
        assert item["inspection_id"] is not None
        assert item["crop_reference"].startswith(f"sessions/{session_id}/crops/")
        assert item["confidence"] >= 0.50
        assert item["bounding_box"]["bbox_width"] > 0
        assert item["bounding_box"]["bbox_height"] > 0
        assert item["processing_status"] in ("inspected", "cropped", "detected")

    # 6. Verify individual inspection accessibility and full pipeline results
    first_product = prod_list["products"][0]
    insp_res = await async_client.get(f"/api/v1/inspections/{first_product['inspection_id']}", headers=auth_headers)
    assert insp_res.status_code == 200
    insp_detail = insp_res.json()
    assert insp_detail["id"] == first_product["inspection_id"]
    assert insp_detail["status"] in ("complete", "compliant", "non_compliant", "violation", "review_required", "not_evaluable")
    assert insp_detail["latest_job"] is not None
    assert insp_detail["latest_job"]["status"] == "complete"
