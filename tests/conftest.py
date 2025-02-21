from collections.abc import AsyncGenerator, AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from src.db.session import base_ormar_config
from src.main import app


@pytest.fixture(scope="function", autouse=True)
async def db() -> AsyncGenerator:
    """Database connection for tests"""
    if not base_ormar_config.database.is_connected:
        await base_ormar_config.database.connect()
    yield
    if base_ormar_config.database.is_connected:
        await base_ormar_config.database.disconnect()


@pytest.fixture(scope="module")
async def client() -> AsyncIterator[AsyncClient]:
    """Mock async client for testing HTTP requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
