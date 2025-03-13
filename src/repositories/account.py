from ..models.account import Account as AccountModel
from ..repositories.base import CRUDBase
from ..schemas.account import AccountCreate, AccountUpdate


class AccountRepository(CRUDBase[AccountModel, AccountCreate, AccountUpdate]):
    """Repository to handle account-related database operations."""

    async def get_by_email(self, email: str) -> AccountModel | None:
        """Retrieve an account by email."""
        return await self.model.objects.filter(email=email).get_or_none()

    def is_active(self, account: AccountModel) -> bool:
        """Check if account is active."""
        return account.is_active


account = AccountRepository(AccountModel)
