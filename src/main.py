"""Main application file for the FastAPI service.

This module initializes the FastAPI application, configures logging,
sets up database connections via a lifespan manager, includes API routers,
and registers custom exception handlers.
"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from http import HTTPStatus

import itsdangerous
import jwt
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse

from .constants.errors import CustomErrorCode
from .controllers import account, auth
from .core.config import settings
from .core.logging import configure_logging
from .db.session import base_ormar_config
from ..schemas.exceptions import APIValidationError, CustomErrorResponse # Corrected typo
from .utils.exceptions import CustomError


def get_lifespan(config: Any) -> callable: # type: ignore[type-arg]
    """Factory function to create a lifespan context manager for FastAPI.

    The lifespan manager handles application startup and shutdown events,
    such as initializing logging and managing database connections.

    Args:
        config (Any): The database configuration object, expected to have
            a `database` attribute with `is_connected`, `connect()`, and
            `disconnect()` methods (e.g., `base_ormar_config`).

    Returns:
        callable: An async context manager function suitable for FastAPI's lifespan.
    """
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        """Manages application startup and shutdown events.

        - Configures logging.
        - Connects to the database if not already connected.
        - Yields control to the application.
        - Disconnects from the database on shutdown if connected.

        Args:
            _app (FastAPI): The FastAPI application instance (often unused in lifespan).
        """
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
                "model": CustomErrorResponse, # Corrected typo
            }
            for code in responses
        },
    },
    title=settings.PROJECT_NAME if hasattr(settings, "PROJECT_NAME") else "FastAPI TDD", # Added title
    version=settings.VERSION if hasattr(settings, "VERSION") else "0.1.0", # Added version
)
app.include_router(account.router, prefix=f"{settings.API_PREFIX}/accounts", tags=["accounts"])
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])


@app.exception_handler(CustomError)
async def custom_error_handler(_request: Any, exc: CustomError) -> ORJSONResponse:
    """Handles custom application errors derived from `CustomError`.

    Args:
        _request (Any): The request that caused the exception (unused).
        exc (CustomError): The instance of the custom error raised.

    Returns:
        ORJSONResponse: A JSON response containing the error code and message.
    """
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Any, exc: RequestValidationError) -> ORJSONResponse:
    """Handles Pydantic RequestValidationErrors.

    Transforms Pydantic's validation errors into a standardized
    `APIValidationError` response.

    Args:
        _request (Any): The request that caused the exception (unused).
        exc (RequestValidationError): The Pydantic validation error instance.

    Returns:
        ORJSONResponse: A JSON response containing structured validation error details.
    """
    return ORJSONResponse(
        content=APIValidationError.from_pydantic(exc).model_dump(exclude_none=True),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.exception_handler(jwt.exceptions.PyJWTError)
async def jwt_exception_handler(_request: Any, exc: jwt.exceptions.PyJWTError) -> ORJSONResponse:
    """Handles exceptions related to JWT authentication errors.

    Catches PyJWTError and its subclasses (like ExpiredSignatureError)
    and returns a standardized 401 error response.

    Args:
        _request (Any): The request that caused the exception (unused).
        exc (jwt.exceptions.PyJWTError): The PyJWTError instance.

    Returns:
        ORJSONResponse: A JSON response indicating a token-related error.
    """
    if isinstance(exc, jwt.exceptions.ExpiredSignatureError):
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, # Use status constant
            content={"error_code": CustomErrorCode.TOKEN_EXPIRED, "message": "Token expired"},
        )
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, # Use status constant
        content={"error_code": CustomErrorCode.INVALID_CREDENTIALS, "message": "Could not validate credentials"},
    )


@app.exception_handler(itsdangerous.exc.BadData)
async def url_safe_token_exception_handler(_request: Any, exc: itsdangerous.exc.BadData) -> ORJSONResponse:
    """Handles exceptions from `itsdangerous` (URL-safe token validation errors).

    Catches `itsdangerous.exc.BadData` and its subclasses (like SignatureExpired)
    and returns a standardized 401 error response.

    Args:
        _request (Any): The request that caused the exception (unused).
        exc (itsdangerous.exc.BadData): The itsdangerous exception instance.

    Returns:
        ORJSONResponse: A JSON response indicating a token-related error.
    """
    if isinstance(exc, itsdangerous.exc.SignatureExpired):
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, # Use status constant
            content={"error_code": CustomErrorCode.TOKEN_EXPIRED, "message": "Token expired"},
        )
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, # Use status constant
        content={"error_code": CustomErrorCode.INVALID_CREDENTIALS, "message": "Could not validate credentials"},
    )
