import pytest
from httpx import AsyncClient
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_argon2_password_hashing():
    password = "SecurePassword123!"
    hashed = AuthService.hash_password(password)
    assert hashed != password
    assert AuthService.verify_password(hashed, password) is True
    assert AuthService.verify_password(hashed, "WrongPassword") is False


@pytest.mark.asyncio
async def test_jwt_token_generation_and_decoding():
    data = {"sub": "user-123", "role": "officer"}
    token = AuthService.create_access_token(data)
    decoded = AuthService.decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "officer"
    assert decoded["type"] == "access"


@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient):
    reg_data = {
        "email": "newuser@lm.gov.in",
        "password": "Password123!",
        "name": "New Officer",
        "role": "officer"
    }
    reg_resp = await async_client.post("/api/v1/auth/register", json=reg_data)
    assert reg_resp.status_code == 201
    user_json = reg_resp.json()
    assert user_json["email"] == "newuser@lm.gov.in"

    # Login
    login_data = {
        "email": "newuser@lm.gov.in",
        "password": "Password123!"
    }
    login_resp = await async_client.post("/api/v1/auth/login", json=login_data)
    assert login_resp.status_code == 200
    token_json = login_resp.json()
    assert "access_token" in token_json
    assert "refresh_token" in token_json

    # Test /auth/me
    headers = {"Authorization": f"Bearer {token_json['access_token']}"}
    me_resp = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "newuser@lm.gov.in"


@pytest.mark.asyncio
async def test_invalid_login(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/auth/login", json={"email": "nonexistent@lm.gov.in", "password": "wrong"})
    assert resp.status_code == 401
