import pytest
from httpx import AsyncClient
from app.services.storage_service import StorageService


@pytest.mark.asyncio
async def test_sha256_hashing():
    data = b"LabelSetu test evidence file contents"
    computed = StorageService.compute_sha256(data)
    assert len(computed) == 64
    assert computed == StorageService.compute_sha256(data)


@pytest.mark.asyncio
async def test_upload_url_generation(async_client: AsyncClient, auth_headers: dict):
    # 1. Create inspection first
    insp_resp = await async_client.post("/api/v1/inspections", json={"product_name": "Test Item"}, headers=auth_headers)
    insp_id = insp_resp.json()["id"]

    req_data = {
        "filename": "label_sample.jpg",
        "mime_type": "image/jpeg",
        "file_size": 204850,
        "sha256_hash": "60e1d8ee1c3e3870dc7fe9ceea1ee55dfecddfb051d95015b6d9d10e53a39e80",
        "width": 1920,
        "height": 1080,
        "gps_latitude": 19.0760,
        "gps_longitude": 72.8777
    }

    resp = await async_client.post(f"/api/v1/inspections/{insp_id}/images/upload-url", json=req_data, headers=auth_headers)
    assert resp.status_code == 200
    res = resp.json()
    assert "upload_url" in res
    assert "object_key" in res
    assert res["object_key"].startswith(f"inspections/{insp_id}/")
