from .. import repositories as crud
from ..models.account import Account as AccountModel
from ..schemas.account import AccountCreate


class AccountService:
    """Service for account-related logic."""

    @classmethod
    async def get_account_by_email(cls, email: str) -> AccountModel | None:
        """Retrieve an account by email."""
        return await crud.account.get_by_email(email)

    @classmethod
    async def create_account_without_auth(cls, account_in: AccountCreate) -> AccountModel:
        """Register a new account without authentication."""
        return await crud.account.create(account_in)

    @classmethod
    async def verify_account(cls, token) -> None:
        """
        Verify an account using the provided token.

        Decode the token to get the account email and mark the account
        as verified if it exists.
        """
        pass
