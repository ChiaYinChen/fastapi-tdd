from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterator
from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.config import settings
from src.core.logging import configure_logging
from src.core.security import get_password_hash
from src.db.session import base_ormar_config
from src.dependencies.auth import RoleChecker
from src.main import app
from src.models.account import Account as AccountModel
from src.services.auth import AuthService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator:
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


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Set custom logging handler for tests."""
    configure_logging()


@pytest.fixture(scope="session")
async def normal_user_token_headers() -> dict[str, str]:
    """Token headers for normal user."""
    auth_token = AuthService.create_access_token(sub=settings.TEST_ACCOUNT_EMAIL)
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
async def authenticated_member(mocker: MockerFixture) -> AccountModel:
    """Mock authenticated member for dependency injection."""
    mock_account = AccountModel(
        email=settings.TEST_ACCOUNT_EMAIL,
        hashed_password=get_password_hash(settings.TEST_ACCOUNT_PASSWORD),
        name=settings.TEST_ACCOUNT_NAME,
    )
    mocker.patch("src.dependencies.auth.crud.account.get_by_email", return_value=mock_account)
    checker = RoleChecker(["MEMBER"])
    return checker(mock_account)
