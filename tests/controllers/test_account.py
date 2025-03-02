"""Unit tests for account API endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from src.controllers.account import email_sender
from src.core.config import settings
from src.models.account import Account as AccountModel
from src.schemas.account import AccountCreate
from src.services.account import AccountService
from tests.utils.validator import is_valid_time_format

if TYPE_CHECKING:
    from httpx import AsyncClient
    from pytest_mock import MockerFixture


async def test_register_account_success(client: AsyncClient, mocker: MockerFixture) -> None:
    """Test response format of `/api/accounts` endpoint for register a new account."""
    mock_send_email = mocker.patch.object(email_sender, "send", new=AsyncMock(return_value=None))
    account_in = AccountCreate(email=settings.TEST_ACCOUNT_EMAIL, password=settings.TEST_ACCOUNT_PASSWORD)
    resp = await client.post("/api/accounts", json=account_in.model_dump())
    created_account = resp.json()
    assert resp.status_code == 201
    assert isinstance(created_account.get("data"), dict)
    created_account = created_account.get("data")
    assert set(created_account.keys()) == {"id", "email", "name", "is_active", "created_at", "updated_at"}
    assert isinstance(created_account["id"], str)
    assert isinstance(created_account["email"], str)
    assert isinstance(created_account["is_active"], bool)
    assert isinstance(created_account["created_at"], str)
    assert isinstance(created_account["updated_at"], str)
    assert is_valid_time_format(created_account["created_at"])
    assert is_valid_time_format(created_account["updated_at"])
    mock_send_email.assert_called_once_with(recipients=[created_account["email"]])


async def test_register_existing_account(client: AsyncClient, mocker: MockerFixture) -> None:
    """Test response format of `/api/accounts` endpoint for register an existing account."""
    account_in = AccountCreate(email=settings.TEST_ACCOUNT_EMAIL, password=settings.TEST_ACCOUNT_PASSWORD)
    mock_account = AccountModel(email=account_in.email, hashed_password=account_in.hashed_password)
    mocker.patch.object(AccountService, "get_account_by_email", new=AsyncMock(return_value=mock_account))
    resp = await client.post("/api/accounts", json=account_in.model_dump())
    created_account = resp.json()
    assert resp.status_code == 409
    assert created_account["error_code"] == "1002"
    assert created_account["message"] == "Email already registered"
    AccountService.get_account_by_email.assert_called_once()


async def test_password_invalid_length(client: AsyncClient) -> None:
    """Test response of `/api/accounts` endpoint for invalid password length."""
    data = {"email": "hello@example.com", "password": "pass"}
    resp = await client.post("/api/accounts", json=data)
    created_account = resp.json()
    assert resp.status_code == 400
    assert created_account["error_code"] == "0000"
