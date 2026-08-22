import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_inspections(async_client: AsyncClient, auth_headers: dict):
    # 1. Create unique inspection
    await async_client.post("/api/v1/inspections", json={"product_name": "Unique Search Product Alpha"}, headers=auth_headers)

    # 2. Query search API
    resp = await async_client.get("/api/v1/search?q=Unique Search Product Alpha", headers=auth_headers)
    assert resp.status_code == 200
    res = resp.json()
    assert res["total_results"] >= 1
    assert any(i["product_name"] == "Unique Search Product Alpha" for i in res["results"])
