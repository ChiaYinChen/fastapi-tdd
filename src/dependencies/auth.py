from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import repositories as crud
from ..constants.errors import CustomErrorCode
from ..core.security import decode_token
from ..models.account import Account as AccountModel
from ..utils import exceptions as exc

security = HTTPBearer(auto_error=False)


async def get_account_from_token(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> AccountModel | None:
    """Retrieve the account with a valid access token."""
    if credentials is None:
        return None
    # decode token and ensure it is of type 'access'
    token_data = decode_token(token=credentials.credentials)
    if token_data.type != "access":
        raise exc.UnauthenticatedError(CustomErrorCode.INVALID_TOKEN_TYPE, "Invalid token type")
    # check if account is valid
    account = await crud.account.get_by_email(email=token_data.sub)
    if not account:
        raise exc.NotFoundError(CustomErrorCode.ENTITY_NOT_FOUND, "Account not found")
    return account


class RoleChecker:
    """Check user permission."""

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: AccountModel | None = Depends(get_account_from_token)):
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


allow_member_only = RoleChecker(["MEMBER"])
AuthenticatedMember = Annotated[AccountModel | None, Depends(allow_member_only)]
