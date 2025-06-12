"""Defines custom error codes used throughout the application.

This module contains enumerations for standardized error codes, allowing for
consistent error identification and handling.
"""
from enum import Enum


class CustomErrorCode(str, Enum):
    """Enumeration of custom error codes.

    Provides a set of specific error codes that can be used by the application
    to signal various error conditions.

    Attributes:
        VALIDATE_ERROR (str): General validation error.
        RESET_PASSWORD_MISMATCH (str): Mismatch between reset password request and user.
        ENTITY_NOT_FOUND (str): Entity not found.
        ENTITY_CONFLICT (str): Conflict between entities in the system.
        NOT_AUTHENTICATED (str): User is not authenticated.
        INVALID_CREDENTIALS (str): Provided credentials are invalid.
        TOKEN_EXPIRED (str): Authentication token has expired.
        INVALID_TOKEN_TYPE (str): Invalid type of authentication token.
        TOKEN_REVOKED (str): Authentication token has been revoked.
        INACTIVE_ACCOUNT (str): Account is inactive.
        OPERATION_NOT_PERMITTED (str): Operation is not permitted for the user.
        INCORRECT_EMAIL_OR_PASSWORD (str): Incorrect email or password.
    """
    # validation errors
    VALIDATE_ERROR = "0000"  # General validation error

    # user-related errors
    RESET_PASSWORD_MISMATCH = "2001"  # Mismatch between reset password request and user

    # entity errors
    ENTITY_NOT_FOUND = "1001"  # Entity not found
    ENTITY_CONFLICT = "1002"  # Conflict between entities in the system

    # auth errors
    NOT_AUTHENTICATED = "4001"  # User is not authenticated
    INVALID_CREDENTIALS = "4002"  # Provided credentials are invalid
    TOKEN_EXPIRED = "4003"  # Authentication token has expired
    INVALID_TOKEN_TYPE = "4004"  # Invalid type of authentication token
    TOKEN_REVOKED = "4005"  # Authentication token has been revoked
    INACTIVE_ACCOUNT = "4006"  # Account is inactive
    OPERATION_NOT_PERMITTED = "4007"  # Operation is not permitted for the user
    INCORRECT_EMAIL_OR_PASSWORD = "4008"  # Incorrect email or password
