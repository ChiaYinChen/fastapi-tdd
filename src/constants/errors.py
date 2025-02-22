from enum import Enum


class CustomErrorCode(str, Enum):
    # validation errors
    VALIDATE_ERROR = "0000"  # General validation error

    # entity errors
    ENTITY_NOT_FOUND = "1001"  # Entity not found
    ENTITY_CONFLICT = "1002"  # Conflict between entities in the system
