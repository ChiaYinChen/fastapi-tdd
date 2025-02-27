"""Unit tests for auth API endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from src.core.config import settings
from src.models.account import Account as AccountModel
from src.schemas.auth import LoginRequest
from src.services.auth import AuthService

if TYPE_CHECKING:
    from httpx import AsyncClient
    from pytest_mock import MockerFixture


async def test_login_via_password(client: AsyncClient, mocker: MockerFixture) -> None:
    """Test response format of `/api/auth/login` endpoint for generate tokens via email/password."""
    login_data = LoginRequest(email=settings.TEST_ACCOUNT_EMAIL, password=settings.TEST_ACCOUNT_PASSWORD)

    # mock authentication and token creation
    mock_account = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password="hashed_password")
    mocker.patch.object(AuthService, "authenticate", new=AsyncMock(return_value=mock_account))
    mocker.patch.object(AuthService, "create_access_token", return_value="mock_access_token")
    mocker.patch.object(AuthService, "create_refresh_token", return_value="mock_refresh_token")

    resp = await client.post("/api/auth/login", json=login_data.model_dump())
    assert resp.status_code == 200
    tokens = resp.json().get("data")
    assert set(tokens.keys()) == {"access_token", "refresh_token", "token_type"}
    assert tokens["access_token"] == "mock_access_token"
    assert tokens["refresh_token"] == "mock_refresh_token"
    assert tokens["token_type"] == "bearer"
    AuthService.authenticate.assert_called_once_with(
        email=settings.TEST_ACCOUNT_EMAIL, password=settings.TEST_ACCOUNT_PASSWORD
    )
    AuthService.create_access_token.assert_called_once()
    AuthService.create_refresh_token.assert_called_once()


async def test_login_with_invalid_password(client: AsyncClient, mocker: MockerFixture) -> None:
    """Test response format of `/api/auth/login` endpoint when login fails with incorrect password."""
    login_data = LoginRequest(email=settings.TEST_ACCOUNT_EMAIL, password="incorrect_password")

    # mock `AuthService.authenticate` to return None (indicating authentication failure)
    mock_authenticate = mocker.patch("src.services.auth.AuthService.authenticate", new=AsyncMock(return_value=None))

    resp = await client.post("/api/auth/login", json=login_data.model_dump())
    tokens = resp.json()
    assert resp.status_code == 401
    assert tokens["error_code"] == "4008"
    assert tokens["message"] == "Incorrect email or password"

    # verify `authenticate` was called once with the correct parameters
    mock_authenticate.assert_called_once_with(email=settings.TEST_ACCOUNT_EMAIL, password="incorrect_password")


async def test_renew_access_token_with_refresh_token(client: AsyncClient, mocker: MockerFixture) -> None:
    """Test response format of `/api/auth/refresh-token` endpoint for renew access token."""
    mock_account = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password="hashed_password")
    valid_refresh_token = AuthService.create_refresh_token(sub=mock_account.email)
    mocker.patch("src.repositories.account.account.get_by_email", return_value=mock_account)
    mocker.patch.object(AuthService, "create_access_token", return_value="mock_new_access_token")
    mocker.patch.object(AuthService, "create_refresh_token", return_value="mock_new_refresh_token")

    resp = await client.post("/api/auth/refresh-token", headers={"Authorization": f"Bearer {valid_refresh_token}"})
    assert resp.status_code == 200

    tokens = resp.json().get("data")
    assert set(tokens.keys()) == {"access_token", "refresh_token", "token_type"}
    assert tokens["access_token"] == "mock_new_access_token"
    assert tokens["refresh_token"] == "mock_new_refresh_token"
    assert tokens["token_type"] == "bearer"
    AuthService.create_access_token.assert_called_once()
    AuthService.create_refresh_token.assert_called_once()
