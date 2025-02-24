from typing import Any

from fastapi import APIRouter, status

from ..schemas.auth import LoginRequest, Token
from ..schemas.response import GenericResponse

router = APIRouter()


@router.post(
    "",
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
    pass
