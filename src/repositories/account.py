from ..models.account import Account as AccountModel
from ..schemas.account import AccountCreate


class AccountRepository:
    """Repository to handle account-related database operations."""

    @classmethod
    async def create(cls, *, obj_in: AccountCreate) -> AccountModel:
        """Create a new account record in the database."""
        pass

    @staticmethod
    def is_active(account: AccountModel) -> bool:
        """Check if account is active."""
        return account.is_active
