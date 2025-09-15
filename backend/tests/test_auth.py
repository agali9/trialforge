import pytest

pytestmark = pytest.mark.asyncio


async def test_register_creates_workspace_and_user(async_client):
    resp = await async_client.post(
        "/auth/register",
        json={"email": "a@b.com", "password": "Password123!", "workspace_name": "WS", "workspace_slug": "ws-1"},
    )
    assert resp.status_code in (200, 400)


async def test_login_returns_jwt(async_client):
    await async_client.post("/auth/register", json={"email": "login@test.com", "password": "Password123!", "workspace_name": "WS", "workspace_slug": "ws-login"})
    resp = await async_client.post("/auth/token", data={"username": "login@test.com", "password": "Password123!"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_protected_route_requires_token(async_client):
    resp = await async_client.get("/experiments")
    assert resp.status_code == 401


async def test_wrong_workspace_returns_403(async_client):
    resp = await async_client.get("/experiments", headers={"Authorization": "Bearer badtoken"})
    assert resp.status_code == 401