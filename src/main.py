from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from http import HTTPStatus

import jwt
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from .constants.errors import CustomErrorCode
from .controllers import account, auth
from .core.config import settings
from .core.logging import configure_logging
from .db.session import base_ormar_config
from .schemas.exceptions import APIValidationError, CustomErrorrResponse
from .utils.exceptions import CustomError


def get_lifespan(config):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # logging settings
        configure_logging()

        # check and establish database connection if not already connected
        if not config.database.is_connected:
            await config.database.connect()

        # yield control back to FastAPI to continue with its startup process
        yield

        # disconnect from the database during shutdown if it was previously connected
        if config.database.is_connected:
            await config.database.disconnect()

    return lifespan


# common response codes
responses: set[int] = {
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
    status.HTTP_404_NOT_FOUND,
    status.HTTP_409_CONFLICT,
    status.HTTP_500_INTERNAL_SERVER_ERROR,
}


app = FastAPI(
    lifespan=get_lifespan(base_ormar_config),
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Validation Error", "model": APIValidationError},
        **{
            code: {
                "description": HTTPStatus(code).phrase,
                "model": CustomErrorrResponse,
            }
            for code in responses
        },
    },
)
app.include_router(account.router, prefix=f"{settings.API_PREFIX}/accounts", tags=["accounts"])
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])


@app.exception_handler(CustomError)
async def custom_error_handler(_, exc: CustomError) -> ORJSONResponse:
    """Handle custom error."""
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError) -> ORJSONResponse:
    """Handle validation exceptions."""
    return ORJSONResponse(
        content=APIValidationError.from_pydantic(exc).model_dump(exclude_none=True),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.exception_handler(jwt.exceptions.PyJWTError)
async def jose_exception_handler(_, exc: jwt.exceptions.PyJWTError) -> ORJSONResponse:
    """Handle jwt exceptions."""
    if isinstance(exc, jwt.exceptions.ExpiredSignatureError):
        return ORJSONResponse(
            status_code=401,
            content={"error_code": CustomErrorCode.TOKEN_EXPIRED, "message": "Token expired"},
        )
    return ORJSONResponse(
        status_code=401,
        content={"error_code": CustomErrorCode.INVALID_CREDENTIALS, "message": "Could not validate credentials"},
    )
