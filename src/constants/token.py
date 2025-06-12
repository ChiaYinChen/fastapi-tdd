"""Defines constants related to token statuses.

This module provides an enumeration for token statuses, specifically for
identifying revoked tokens.
"""
from enum import Enum


class TokenStatus(int, Enum):
    """Enumeration of token statuses.

    Attributes:
        REVOKED (int): Represents the status of a token that has been revoked.
    """
    REVOKED = 40
