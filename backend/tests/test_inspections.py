import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_inspection(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "channel": "Retail store",
        "state": "Maharashtra",
        "district": "Mumbai",
        "product_name": "GlowSoft Lotion",
        "brand_name": "GlowSoft"
    }

    response = await async_client.post("/api/v1/inspections", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["inspection_number"].startswith("LM/")
    assert data["product_name"] == "GlowSoft Lotion"

    inspection_id = data["id"]

    # Get Inspection detail
    get_resp = await async_client.get(f"/api/v1/inspections/{inspection_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    detail = get_resp.json()
    assert detail["id"] == inspection_id
    assert detail["status"] == "draft"
    assert detail["images"] == []


@pytest.mark.asyncio
async def test_list_inspections(async_client: AsyncClient, auth_headers: dict):
    resp = await async_client.get("/api/v1/inspections", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
