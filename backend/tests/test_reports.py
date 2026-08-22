import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_report_generation_and_download(async_client: AsyncClient, auth_headers: dict):
    # 1. Create inspection
    insp_resp = await async_client.post("/api/v1/inspections", json={"product_name": "Report Test Item"}, headers=auth_headers)
    insp_id = insp_resp.json()["id"]

    # 2. Generate PDF report
    rep_resp = await async_client.post(f"/api/v1/inspections/{insp_id}/reports", json={"format": "pdf"}, headers=auth_headers)
    assert rep_resp.status_code == 201
    rep_json = rep_resp.json()

    assert "id" in rep_json
    assert rep_json["format"] == "pdf"
    assert "download_url" in rep_json
    assert len(rep_json["sha256_hash"]) == 64

    report_id = rep_json["id"]

    # 3. Download URL Endpoint
    dl_resp = await async_client.get(f"/api/v1/reports/{report_id}/download", headers=auth_headers)
    assert dl_resp.status_code == 200
    assert "download_url" in dl_resp.json()
