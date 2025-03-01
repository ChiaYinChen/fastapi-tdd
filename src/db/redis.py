import redis

from ..core.config import settings


class RedisClient:
    """Wrapper for Redis client."""

    def __init__(self, db: int = 0, *args, **kwargs):
        """
        Initialize Redis client.

        Args:
            db (int): redis database index
        """
        self.client = redis.from_url(settings.REDIS_URI, db=db, encoding="utf-8", decode_responses=True)

    def get(self, key: str) -> str | None:
        """Get the value of a key in Redis."""
        return self.client.get(key)

    def set(self, key: str, value: str, ttl: int) -> bool:
        """Set a key-value pair in Redis with a specified time-to-live (TTL)."""
        return self.client.set(name=key, value=value, ex=ttl)
