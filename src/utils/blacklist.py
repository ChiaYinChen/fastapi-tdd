from ..constants.token import TokenStatus
from ..db.redis import RedisClient


class TokenBlackList:
    """Store the revoked token in Redis."""

    def __init__(self, db: int, *args, **kwargs):
        """Initialize Redis connection pool."""
        self.client = RedisClient(db=db)

    def get(self, token: str) -> str | None:
        """Check if a token has been revoked."""
        return self.client.get(token)

    def save(self, token: str, ttl: int) -> None:
        """Set the token as invalid."""
        self.client.set(token, TokenStatus.REVOKED.value, ttl)
