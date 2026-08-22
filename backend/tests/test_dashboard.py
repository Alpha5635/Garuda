import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_overview(async_client: AsyncClient, auth_headers: dict):
    resp = await async_client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert resp.status_code == 200
    res = resp.json()

    assert "total_inspections" in res
    assert "total_violations" in res
    assert "compliance_rate_percent" in res
    assert "district_metrics" in res
