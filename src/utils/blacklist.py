"""Manages a blacklist for JWT tokens using Redis.

This module provides the `TokenBlackList` class, which uses a Redis client
to store and check for revoked tokens, typically identified by their JTI (JWT ID).
"""
from ..constants.token import TokenStatus
from ..db.redis import RedisClient


class TokenBlackList:
    """Manages a blacklist of revoked tokens stored in Redis.

    This class provides methods to add tokens to the blacklist (marking them as
    revoked) and to check if a token is currently in the blacklist.

    Attributes:
        client (RedisClient): An instance of `RedisClient` used to interact
            with the Redis database.
    """

    def __init__(self, db: int, *args, **kwargs):
        """Initializes the TokenBlackList with a Redis client.

        Args:
            db (int): The Redis database index to use for the blacklist.
            *args: Additional arguments to pass to the `RedisClient` constructor.
            **kwargs: Additional keyword arguments to pass to the `RedisClient` constructor.
        """
        self.client = RedisClient(db=db, *args, **kwargs)

    def get(self, token: str) -> str | None:
        """Checks if a token (JTI) is in the blacklist.

        Args:
            token (str): The token identifier (e.g., JTI) to check.

        Returns:
            str | None: The status of the token (e.g., "40" for revoked) if found
                in the blacklist, otherwise None.
        """
        return self.client.get(token)

    def save(self, token: str, ttl: int) -> None:
        """Adds a token (JTI) to the blacklist with a specified TTL.

        Marks the token as revoked by storing its JTI with a specific status value.

        Args:
            token (str): The token identifier (e.g., JTI) to blacklist.
            ttl (int): The time-to-live for the blacklist entry in seconds.
        """
        self.client.set(token, TokenStatus.REVOKED.value, ttl)
