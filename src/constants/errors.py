from enum import Enum


class CustomErrorCode(str, Enum):
    # validation errors
    VALIDATE_ERROR = "0000"  # General validation error

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
