"""Repository for account data operations.

This module provides the `AccountRepository` class, which encapsulates
database operations related to user accounts, extending the generic `CRUDBase`.
It includes methods for retrieving accounts by email and checking account status.

Attributes:
    account (AccountRepository): A singleton instance of the AccountRepository.
"""
from ..models.account import Account as AccountModel
from ..repositories.base import CRUDBase
from ..schemas.account import AccountCreate, AccountUpdate


class AccountRepository(CRUDBase[AccountModel, AccountCreate, AccountUpdate]):
    """Repository for handling account-related database operations.

    This class provides specific methods for account data manipulation,
    such as finding an account by email or checking its active status,
    in addition to the generic CRUD operations inherited from `CRUDBase`.
    """

    async def get_by_email(self, email: str) -> AccountModel | None:
        """Retrieves an account by its email address.

        Args:
            email (str): The email address of the account to retrieve.

        Returns:
            AccountModel | None: The account model if found, otherwise None.
        """
        return await self.model.objects.filter(email=email).get_or_none()

    def is_active(self, account: AccountModel) -> bool:
        """Checks if an account is active.

        Args:
            account (AccountModel): The account model instance to check.

        Returns:
            bool: True if the account is active, False otherwise.
        """
        return account.is_active


account = AccountRepository(AccountModel)
