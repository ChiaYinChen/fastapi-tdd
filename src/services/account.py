from datetime import datetime

from .. import repositories as crud
from ..constants.errors import CustomErrorCode
from ..core.config import settings
from ..core.security import decode_url_safe_token
from ..models.account import Account as AccountModel
from ..schemas.account import AccountCreate, ResetPassword
from ..utils import exceptions as exc


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
        token_data = decode_url_safe_token(token, max_age=settings.URL_SAFE_TOKEN_TTL)
        account = await crud.account.get_by_email(token_data["email"])
        if not account:
            raise exc.NotFoundError(CustomErrorCode.ENTITY_NOT_FOUND, "Account not found")
        await crud.account.update(db_obj=account, obj_in={"is_verified": True, "verified_at": datetime.now()})

    @classmethod
    async def reset_password(cls, account_obj: AccountModel, pwd_in: ResetPassword) -> AccountModel:
        """Reset the user's password."""
        pass
