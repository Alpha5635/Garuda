import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ecommerce_listing_evaluation(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "platform": "Amazon",
        "listing_id": "B08N5WRWNW",
        "url": "https://www.amazon.in/dp/B08N5WRWNW",
        "seller_name": "GlowSoft Official Retail",
        "declarations": {
            "manufacturer": "GlowSoft Skincare Pvt. Ltd.",
            "net_quantity": "400 g",
            "mrp": "MRP Rs. 249.00 (Incl. of all taxes)",
            "consumer_care": "1800-111-222"
        }
    }

    resp = await async_client.post("/api/v1/ecommerce/listings", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    res = resp.json()

    assert res["platform"] == "Amazon"
    assert len(res["content_hash"]) == 64
    assert len(res["rule_evaluations"]) > 0

    # Verify Rule 6(10) month/year exemption -> result is 'not_applicable'
    month_year_rule = next(r for r in res["rule_evaluations"] if r["rule_id"] == "LM-6-1-D-01")
    assert month_year_rule["result"] == "not_applicable"
