from ..db.redis import RedisClient


class TokenBlackList:
    """Store the revoked token in Redis."""

    def __init__(self, db: int, *args, **kwargs):
        """Initialize Redis connection pool."""
        self.client = RedisClient(db=db)

    def get(self, token: str) -> str | None:
        """Check if a token has been revoked."""
        pass

    def save(self, token: str, ttl: int) -> None:
        """Set the token as invalid."""
        pass
