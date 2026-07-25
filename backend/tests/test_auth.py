import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    payload = {
        "name": "Test Student",
        "email": "student@example.com",
        "password": "Password123!",
        "college": "MIT",
        "branch": "Computer Science",
        "year": "3rd Year",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["name"] == payload["name"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "name": "Test Student",
        "email": "duplicate@example.com",
        "password": "Password123!",
    }
    resp1 = await client.post("/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/auth/register", json=payload)
    assert resp2.status_code == 400
    assert "Email already registered" in resp2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success_and_fail(client: AsyncClient):
    reg_payload = {
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "SecretPassword123",
    }
    await client.post("/auth/register", json=reg_payload)

    # Valid Login
    login_resp = await client.post(
        "/auth/login",
        json={"email": reg_payload["email"], "password": reg_payload["password"]},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # Invalid Password
    fail_resp = await client.post(
        "/auth/login",
        json={"email": reg_payload["email"], "password": "WrongPassword"},
    )
    assert fail_resp.status_code == 401
