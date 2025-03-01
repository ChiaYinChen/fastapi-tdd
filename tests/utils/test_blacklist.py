from src.core.config import settings
from src.utils.blacklist import TokenBlackList

token_blacklist = TokenBlackList(db=settings.TEST_REDIS_DB)


async def test_save_and_get_revoked_token():
    """Test storing and retrieving revoked token."""
    test_token = "revoked_token"
    assert token_blacklist.get(test_token) is None

    token_blacklist.save(test_token, 5)  # 5 seconds
    assert token_blacklist.get(test_token) == "1"
