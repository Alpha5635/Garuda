import uuid
import pytest
from httpx import AsyncClient
from app.services.auth_service import AuthService
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_rule_pack_admin_workflow(async_client: AsyncClient, auth_headers: dict):
    # 1. List rule packs
    list_resp = await async_client.get("/api/v1/rule-packs", headers=auth_headers)
    assert list_resp.status_code == 200
    assert isinstance(list_resp.json(), list)

    # 2. Create rule_admin user headers
    admin_token = AuthService.create_access_token(
        data={"sub": str(uuid.uuid4()), "role": UserRole.RULE_ADMIN.value, "email": "ruleadmin@doca.gov.in"}
    )
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Register admin user in test session if needed or test token payload
    staged_payload = {
        "version": f"rp-2026.{uuid.uuid4().hex[:4]}",
        "name": "Stage Test Rule Pack",
        "rules_json": {"test": True}
    }

    # Officer request returns 403 forbidden
    officer_resp = await async_client.post("/api/v1/rule-packs", json=staged_payload, headers=auth_headers)
    assert officer_resp.status_code == 403

    # Register admin user via register endpoint
    admin_reg = {
        "email": f"ruleadmin_{uuid.uuid4().hex[:4]}@doca.gov.in",
        "password": "Password@123",
        "name": "Rule Admin",
        "role": "rule_admin"
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=admin_reg)
    assert reg_res.status_code == 201

    login_res = await async_client.post("/api/v1/auth/login", json={"email": admin_reg["email"], "password": "Password@123"})
    admin_token_res = login_res.json()["access_token"]
    valid_admin_headers = {"Authorization": f"Bearer {admin_token_res}"}

    create_resp = await async_client.post("/api/v1/rule-packs", json=staged_payload, headers=valid_admin_headers)
    assert create_resp.status_code == 201
    pack = create_resp.json()
    assert pack["status"] == "staged"
