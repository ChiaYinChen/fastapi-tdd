"""Unit tests for account service logic."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import itsdangerous
import pytest

from src import repositories as crud
from src.core.config import settings
from src.core.security import decode_url_safe_token, encode_url_safe_token
from src.models.account import Account as AccountModel
from src.schemas.account import AccountCreate
from src.services.account import AccountService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


async def test_create_account_without_auth() -> None:
    """Test for create account without authentication."""
    account_in = AccountCreate(
        email=settings.TEST_ACCOUNT_EMAIL, password=settings.TEST_ACCOUNT_PASSWORD, name=settings.TEST_ACCOUNT_NAME
    )
    assert isinstance(account_in.email, str)
    assert isinstance(account_in.hashed_password, str)
    assert isinstance(account_in.name, str)
    account = await AccountService.create_account_without_auth(account_in)
    assert isinstance(account, AccountModel)
    assert account.name == settings.TEST_ACCOUNT_NAME


async def test_get_account_by_email(mocker: MockerFixture) -> None:
    """Test for create account without authentication."""
    mock_account = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password=settings.TEST_ACCOUNT_PASSWORD)
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=mock_account))
    assert isinstance(mock_account.email, str)
    account = await AccountService.get_account_by_email(email=mock_account.email)
    assert isinstance(account, AccountModel)
    assert account.email == settings.TEST_ACCOUNT_EMAIL


async def test_get_account_by_email_not_found(mocker: MockerFixture) -> None:
    """Test for retrieve account with email that doesn't exist."""
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=None))
    account = await AccountService.get_account_by_email(email="not_exists@example.com")
    assert account is None


async def test_verify_account(mocker: MockerFixture) -> None:
    """Test account verification logic in `AccountService.verify_account`."""
    mock_token_data = {"email": settings.TEST_ACCOUNT_EMAIL}
    mock_decode_token = mocker.patch("src.services.account.decode_url_safe_token", return_value=mock_token_data)
    mock_account = AccountModel(email=mock_token_data["email"], hashed_password=settings.TEST_ACCOUNT_PASSWORD)
    assert mock_account.is_verified is False
    assert mock_account.verified_at is None
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=mock_account))
    await AccountService.verify_account(token="mock_token")
    mock_decode_token.assert_called_once_with("mock_token", max_age=settings.URL_SAFE_TOKEN_TTL)
    assert mock_account.email == mock_token_data["email"]
    assert mock_account.is_verified is True
    assert isinstance(mock_account.verified_at, datetime)


def test_verify_account_with_expired_token() -> None:
    """Test account verification failure due to expired token."""
    mock_token = encode_url_safe_token({"email": settings.TEST_ACCOUNT_EMAIL})
    with pytest.raises(itsdangerous.exc.SignatureExpired):
        decode_url_safe_token(mock_token, max_age=-1)
