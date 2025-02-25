from typing import Any

from fastapi import APIRouter, status

from ..constants.errors import CustomErrorCode
from ..schemas.auth import LoginRequest, Token
from ..schemas.response import GenericResponse
from ..services.auth import AuthService
from ..utils import exceptions as exc

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
