import os
import sys

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BACKEND_DIR)

from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Create DB schema before any tests hit the API."""
    cfg = Config(os.path.join(BACKEND_DIR, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "alembic"))
    command.upgrade(cfg, "head")


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_user(async_client):
    email = "test@example.com"
    password = "Password123!"
    await async_client.post(
        "/auth/register",
        json={"email": email, "password": password, "workspace_name": "Test", "workspace_slug": "test"},
    )
    token = await async_client.post("/auth/token", data={"username": email, "password": password})
    return token.json()["access_token"]
