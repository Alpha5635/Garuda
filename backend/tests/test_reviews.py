import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ocr_correction_submission(async_client: AsyncClient, auth_headers: dict):
    # 1. Create inspection
    insp_resp = await async_client.post("/api/v1/inspections", json={"product_name": "Review Item"}, headers=auth_headers)
    insp_id = insp_resp.json()["id"]

    # 2. Submit OCR correction
    corr_data = {
        "field_name": "net_quantity",
        "original_ocr_value": "500g",
        "corrected_value": "500 g",
        "reason": "Officer corrected missing spacing between 500 and g"
    }

    resp = await async_client.post(f"/api/v1/reviews/inspections/{insp_id}/ocr-correction", json=corr_data, headers=auth_headers)
    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] == "success"
    assert "updated_record_id" in res
