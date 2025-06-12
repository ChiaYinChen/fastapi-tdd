"""Provides a Redis client wrapper for interacting with a Redis server.

This module defines the `RedisClient` class, which simplifies connecting to
and performing common operations (GET, SET with TTL) on a Redis database
using the application's settings.
"""
import redis

from ..core.config import settings


class RedisClient:
    """A wrapper for the Redis client providing basic GET and SET operations.

    This class initializes a connection to a Redis server using a URL specified
    in the application settings. It allows interaction with a specific Redis database.

    Attributes:
        client (redis.Redis): The underlying Redis client instance.
    """

    def __init__(self, db: int = 0, *args, **kwargs):
        """Initializes the RedisClient.

        Connects to a Redis instance using the application's Redis URI and
        a specified database index.

        Args:
            db (int): The Redis database index to connect to. Defaults to 0.
            *args: Additional arguments to pass to the Redis client.
            **kwargs: Additional keyword arguments to pass to the Redis client.
        """
        self.client = redis.from_url(settings.REDIS_URI, db=db, encoding="utf-8", decode_responses=True, *args, **kwargs)

    def get(self, key: str) -> str | None:
        """Gets the value of a key in Redis.

        Args:
            key (str): The key whose value is to be retrieved.

        Returns:
            str | None: The value of the key if it exists, otherwise None.
        """
        return self.client.get(key)

    def set(self, key: str, value: str, ttl: int) -> bool | None:
        """Sets a key-value pair in Redis with a specified time-to-live (TTL).

        Args:
            key (str): The key to set.
            value (str): The value to associate with the key.
            ttl (int): The time-to-live for the key in seconds.

        Returns:
            bool | None: True if the key was set successfully, None otherwise (some clients might return None).
        """
        return self.client.set(name=key, value=value, ex=ttl)
