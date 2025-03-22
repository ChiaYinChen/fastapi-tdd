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
from src.schemas.account import AccountCreate, AccountUpdate, ResetPassword
from src.services.account import AccountService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


async def test_create_account_without_auth(db_session) -> None:
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


async def test_verify_account(db_session, mocker: MockerFixture) -> None:
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


async def test_reset_password(mocker: MockerFixture) -> None:
    """Test reset password logic in `AccountService.reset_password`."""
    # Arrange: prepare input data for password reset
    pwd_in = ResetPassword(current_password="mock_old_password", new_password="mock_new_password")
    mock_with_old_pwd = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password="mock_old_hash_password")

    # Arrange: mock the AccountUpdate object with the new password
    mock_updated_in = AccountUpdate(password=pwd_in.new_password)
    assert "$pbkdf2-sha256" in mock_updated_in.hashed_password
    mocker.patch("src.services.account.AccountUpdate", return_value=mock_updated_in)

    # Arrange: mock the updated account object
    mock_with_new_pwd = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password=mock_updated_in.hashed_password)
    mocker.patch.object(crud.account, "update", new=AsyncMock(return_value=mock_with_new_pwd))

    # Act: call the function under test
    result = await AccountService.reset_password(account_obj=mock_with_old_pwd, pwd_in=pwd_in)

    # Assert: verify the expected behavior
    crud.account.update.assert_called_once_with(db_obj=mock_with_old_pwd, obj_in=mock_updated_in)
    assert result == mock_with_new_pwd
    assert result.hashed_password == mock_updated_in.hashed_password
    assert result.email == settings.TEST_ACCOUNT_EMAIL
