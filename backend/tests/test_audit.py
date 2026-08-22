import uuid
import pytest
from httpx import AsyncClient
from app.services.audit_service import AuditService


def test_audit_hash_chain_calculation():
    service = AuditService()
    prev_hash = "GENESIS_HASH_00000000000000000000000000000000000000000000000000000000"
    payload = {"action": "INSPECTION_CREATED", "entity_id": "123", "actor": "officer@lm.gov.in"}

    h1 = service.compute_event_hash(prev_hash, payload)
    assert len(h1) == 64

    # Tampering payload changes hash
    tampered_payload = {"action": "INSPECTION_CREATED", "entity_id": "123", "actor": "hacker@evil.example"}
    h_tampered = service.compute_event_hash(prev_hash, tampered_payload)
    assert h1 != h_tampered


@pytest.mark.asyncio
async def test_audit_verification_endpoint(async_client: AsyncClient, auth_headers: dict):
    # 1. Create inspection
    insp_resp = await async_client.post("/api/v1/inspections", json={"product_name": "Audit Test Item"}, headers=auth_headers)
    insp_id = insp_resp.json()["id"]

    # 2. Verify audit chain
    verify_resp = await async_client.get(f"/api/v1/audit/verify/{insp_id}", headers=auth_headers)
    assert verify_resp.status_code == 200
    res = verify_resp.json()
    assert res["intact"] is True
    assert res["algorithm"] == "SHA-256"
