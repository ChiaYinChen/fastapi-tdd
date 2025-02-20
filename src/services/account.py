from ..models.account import Account as AccountModel
from ..schemas.account import AccountCreate


class AccountService:
    """Service for account-related logic."""

    @classmethod
    async def create_account_without_auth(cls, account_in: AccountCreate) -> AccountModel:
        """Register a new account without authentication."""
        pass
