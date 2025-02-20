"""Unit tests for account service logic."""

from src.models.account import Account as AccountModel
from src.schemas.account import AccountCreate
from src.services.account import AccountService


async def test_create_account_without_auth() -> None:
    """Test for create account without authentication."""
    account_in = AccountCreate(email="hello@gmail.com", password="hellopass")
    account = await AccountService.create_account_without_auth(account_in)
    assert isinstance(account, AccountModel)
