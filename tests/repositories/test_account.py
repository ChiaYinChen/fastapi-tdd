"""Unit tests for CRUD operations related to account logic."""

from src.core.config import settings
from src.models.account import Account as AccountModel
from src.repositories.account import AccountRepository
from src.schemas.account import AccountCreate


async def test_create_account() -> None:
    """Test for create account."""
    account_in = AccountCreate(email=settings.TEST_ACCOUNT_EMAIL, password=settings.TEST_ACCOUNT_PASSWORD)
    account = await AccountRepository.create(obj_in=account_in)
    assert account.email == settings.TEST_ACCOUNT_EMAIL
    assert hasattr(account, "hashed_password")
    assert isinstance(account.hashed_password, str)
    _test_check_if_account_is_active(db_obj=account)


def _test_check_if_account_is_active(*, db_obj: AccountModel) -> None:
    """Test for check if account is active."""
    is_active = AccountRepository.is_active(db_obj)
    assert is_active is True
