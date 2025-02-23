"""Unit tests for account service logic."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from src import repositories as crud
from src.core.config import settings
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
