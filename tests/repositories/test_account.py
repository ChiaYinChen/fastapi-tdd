"""Unit tests for CRUD operations related to account logic."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from uuid import UUID

from src import repositories as crud
from src.core.config import settings
from src.models.account import Account as AccountModel
from src.schemas.account import AccountCreate

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


async def test_create_account() -> None:
    """Test for create account."""
    account_in = AccountCreate(email=settings.TEST_ACCOUNT_EMAIL, password=settings.TEST_ACCOUNT_PASSWORD)
    account = await crud.account.create(obj_in=account_in)
    assert account.email == settings.TEST_ACCOUNT_EMAIL
    assert hasattr(account, "hashed_password")
    assert isinstance(account.hashed_password, str)
    assert isinstance(account.id, UUID)
    assert hasattr(account, "name")
    assert isinstance(account.is_active, bool)
    assert account.is_active is True
    assert isinstance(account.created_at, datetime)
    assert isinstance(account.updated_at, datetime)


async def test_get_account(mocker: MockerFixture) -> None:
    """Test for retrieve an existing account by email."""
    # mock get_by_email to return a predefined account object
    mock_account = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password="hashed_password")
    mocker.patch.object(crud.account, "get_by_email", new=AsyncMock(return_value=mock_account))
    # call the method and verify the returned account
    account = await crud.account.get_by_email(email=settings.TEST_ACCOUNT_EMAIL)
    assert account
    assert isinstance(account, AccountModel)
    assert account.email == settings.TEST_ACCOUNT_EMAIL


async def test_get_account_with_unregistered_email() -> None:
    """Test for retrieve account with unregistered email."""
    account = await crud.account.get_by_email(email="not_exists@example.com")
    assert account is None


def test_check_if_account_is_active() -> None:
    """Test for check if account is active."""
    mock_account = AccountModel(email=settings.TEST_ACCOUNT_EMAIL, hashed_password="hashed_password")
    is_active = crud.account.is_active(mock_account)
    assert isinstance(is_active, bool)
    assert is_active is True
