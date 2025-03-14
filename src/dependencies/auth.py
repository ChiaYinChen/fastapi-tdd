from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import repositories as crud
from ..constants.errors import CustomErrorCode
from ..core.config import settings
from ..core.security import decode_token
from ..models.account import Account as AccountModel
from ..schemas.auth import TokenPayload
from ..utils import exceptions as exc
from ..utils.blacklist import TokenBlackList

blacklist = TokenBlackList(db=settings.BLACK_LIST_REDIS_DB)


class TokenBearer(HTTPBearer):
    """Handle token authentication using HTTP Bearer token."""

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> TokenPayload | None:
        """Validate the token from the request."""
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if not credentials:
            return None
        token_data = decode_token(token=credentials.credentials)
        if not self.validate_token_data(token_data):
            raise exc.UnauthenticatedError(CustomErrorCode.INVALID_TOKEN_TYPE, "Invalid token type")
        return token_data

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Validate the token type."""
        raise NotImplementedError("Subclasses must implement this method")


class AccessTokenBearer(TokenBearer):
    """Handle access token validation."""

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Check if the token is an access token."""
        return True if token_data.type == "access" else False


class RefreshTokenBearer(TokenBearer):
    """Handle refresh token validation."""

    def validate_token_data(self, token_data: TokenPayload) -> bool:
        """Check if the token is a refresh token and ensure it has not been revoked."""
        if token_data.type != "refresh":
            return False
        if self.is_token_revoked(token_data.jti):
            raise exc.UnauthenticatedError(CustomErrorCode.TOKEN_REVOKED, "Token revoked")
        return True

    def is_token_revoked(self, jti: str) -> bool:
        """Check if the token has been revoked."""
        return True if blacklist.get(token=jti) else False


async def get_account_from_access_token(
    token_data: TokenPayload | None = Depends(AccessTokenBearer(auto_error=False)),
) -> AccountModel | None:
    """Retrieve the account using an access token."""
    if not token_data:
        return None
    account = await crud.account.get_by_email(email=token_data.sub)
    if not account:
        raise exc.NotFoundError(CustomErrorCode.ENTITY_NOT_FOUND, "Account not found")
    return account


async def get_account_from_refresh_token(
    token_data: TokenPayload | None = Depends(RefreshTokenBearer(auto_error=False)),
) -> AccountModel:
    """Retrieve the account using a refresh token."""
    if not token_data:
        raise exc.UnauthenticatedError(CustomErrorCode.NOT_AUTHENTICATED, "Not authenticated")
    blacklist.save(token=token_data.jti, ttl=settings.REFRESH_TOKEN_TTL)
    account = await crud.account.get_by_email(email=token_data.sub)
    if not account:
        raise exc.NotFoundError(CustomErrorCode.ENTITY_NOT_FOUND, "Account not found")
    return account


class RoleChecker:
    """Check user permission."""

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: AccountModel | None = Depends(get_account_from_access_token)):
        """
        Validate the user's permission for a specific operation.

        - If authentication is required but no user is provided, raise UnauthenticatedError.
        - If the user is authenticated but does not have the required authorization role, raise UnauthorizedError.
        - If the user is authenticated and has the required authorization role, return the current_user object.
        """
        # require authentication unless 'GUEST' access is allowed
        if "GUEST" not in self.allowed_roles and not current_user:
            raise exc.UnauthenticatedError(CustomErrorCode.NOT_AUTHENTICATED, "Not authenticated")
        # check if user has the required authorization
        # TODO: implement role-based permission checking logic
        if current_user:
            if not crud.account.is_active(current_user):
                raise exc.UnauthorizedError(CustomErrorCode.OPERATION_NOT_PERMITTED, "Operation not permitted")
            return current_user
        # allow guest access
        return None


AuthenticatedMember = Annotated[AccountModel | None, Depends(RoleChecker(["MEMBER"]))]
