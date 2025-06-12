"""Service layer for account-related business logic.

This module provides the `AccountService` class, which encapsulates
business logic for operations such as account creation, verification,
password management, and retrieval. It acts as an intermediary between
the API layer (controllers) and the data access layer (repositories).
"""
from datetime import datetime

from .. import repositories as crud
from ..constants.errors import CustomErrorCode
from ..core.config import settings
from ..core.security import decode_url_safe_token
from ..models.account import Account as AccountModel
from ..schemas.account import AccountCreate, AccountUpdate, ResetPassword
from ..utils import exceptions as exc


class AccountService:
    """Provides business logic services related to user accounts."""

    @classmethod
    async def get_account_by_email(cls, email: str) -> AccountModel | None:
        """Retrieves an account by its email address.

        Args:
            email (str): The email address of the account to retrieve.

        Returns:
            AccountModel | None: The account model if found, otherwise None.
        """
        return await crud.account.get_by_email(email)

    @classmethod
    async def create_account_without_auth(cls, account_in: AccountCreate) -> AccountModel:
        """Creates a new user account.

        This method is typically used for initial user registration.

        Args:
            account_in (AccountCreate): The Pydantic schema containing data for the new account.

        Returns:
            AccountModel: The newly created account model instance.
        """
        return await crud.account.create(account_in)

    @classmethod
    async def verify_account(cls, token: str) -> None:
        """Verifies a user's account using a URL-safe timed token.

        Decodes the provided token to extract the user's email, retrieves the account,
        and marks it as verified.

        Args:
            token (str): The URL-safe timed token sent to the user for verification.

        Raises:
            itsdangerous.SignatureExpired: If the token has expired.
            itsdangerous.BadTimeSignature: If the token signature is invalid or malformed.
            itsdangerous.BadSignature: If the token signature is invalid.
            exc.NotFoundError: If the account associated with the token is not found.
        """
        token_data = decode_url_safe_token(token, max_age=settings.URL_SAFE_TOKEN_TTL)
        account = await crud.account.get_by_email(token_data["email"])
        if not account:
            raise exc.NotFoundError(CustomErrorCode.ENTITY_NOT_FOUND, "Account not found")
        await crud.account.update(db_obj=account, obj_in={"is_verified": True, "verified_at": datetime.now(datetime.UTC)})

    @classmethod
    async def reset_password(cls, account_obj: AccountModel, pwd_in: ResetPassword) -> AccountModel:
        """Resets a user's password.

        Args:
            account_obj (AccountModel): The account model instance for which to reset the password.
            pwd_in (ResetPassword): A Pydantic schema containing the new password.
                Note: This schema typically includes current_password for validation
                at the controller level, but only new_password is used here for the update.

        Returns:
            AccountModel: The updated account model instance with the new password.
        """
        # Assuming AccountUpdate schema can handle password-only updates
        # and that `hashed_password` field in AccountUpdate will hash it.
        updated_account_data = AccountUpdate(password=pwd_in.new_password)
        return await crud.account.update(db_obj=account_obj, obj_in=updated_account_data)
