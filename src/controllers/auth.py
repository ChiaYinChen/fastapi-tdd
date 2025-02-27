from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends, status

from ..constants.errors import CustomErrorCode
from ..dependencies.auth import get_account_from_refresh_token
from ..schemas.auth import LoginRequest, Token
from ..schemas.response import GenericResponse
from ..services.auth import AuthService
from ..utils import exceptions as exc

if TYPE_CHECKING:
    from ..models.account import Account as AccountModel

router = APIRouter()


@router.post(
    "/login",
    response_model=GenericResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and generate tokens",
)
async def login(login_data: LoginRequest) -> Any:
    """
    Authenticate a user via email and password, then generate access and refresh tokens.

    * access token expires in 15 minutes
    * refresh token expires in 24 hours
    """
    account = await AuthService.authenticate(email=login_data.email, password=login_data.password)
    if not account:
        raise exc.UnauthenticatedError(CustomErrorCode.INCORRECT_EMAIL_OR_PASSWORD, "Incorrect email or password")
    return GenericResponse(
        data=Token(
            access_token=AuthService.create_access_token(sub=account.email),
            refresh_token=AuthService.create_refresh_token(sub=account.email),
            token_type="bearer",
        )
    )


@router.post(
    "/refresh-token",
    response_model=GenericResponse[Token],
    status_code=status.HTTP_200_OK,
)
async def refresh_token(current_user: AccountModel = Depends(get_account_from_refresh_token)) -> Any:
    """
    Renew the user's access token with refresh token.
    """
    return GenericResponse(
        data=Token(
            access_token=AuthService.create_access_token(sub=current_user.email),
            refresh_token=AuthService.create_refresh_token(sub=current_user.email),
            token_type="bearer",
        )
    )
