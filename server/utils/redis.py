import redis.asyncio as redis
from .config import get_settings

settings = get_settings()

REDIS_URL = settings.celery_broker_url  # Example: "redis://localhost:6379/0"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# --- General Cache Utilities ---

async def set_cache(key: str, value: str, expire: int = 3600):
    """Set a value in Redis with an expiration."""
    await redis_client.set(name=key, value=value, ex=expire)

async def get_cache(key: str) -> str | None:
    """Retrieve a value from Redis by key."""
    return await redis_client.get(key)

async def delete_cache(key: str):
    """Delete a key from Redis."""
    await redis_client.delete(key)

async def invalidate_tracked_airdrops_cache(user_id: str):
    """Invalidate all paginated tracked airdrops cache for this user."""
    pattern = f"user:{user_id}:tracked_airdrops*"
    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)

# --- Token Blacklisting for Session/Token Revocation ---

BLACKLIST_PREFIX = "blacklisted_token:"
USER_TOKENS_PREFIX = "user_tokens:"  # For global logout

async def set_blacklisted_token(token: str, expire: int = 60 * 60 * 24 * 7):
    """
    Blacklist a token for a week (default).
    This means the token is no longer valid even if it's not expired.
    """
    await redis_client.set(f"{BLACKLIST_PREFIX}{token}", "1", ex=expire)

async def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.
    """
    return await redis_client.exists(f"{BLACKLIST_PREFIX}{token}") == 1

async def add_user_token(user_id: str, token: str, expire: int = 60 * 60 * 24 * 7):
    """
    Store a token under a user-specific set for global logout later.
    Default expiry: 7 days.
    """
    key = f"{USER_TOKENS_PREFIX}{user_id}"
    await redis_client.sadd(key, token)
    await redis_client.expire(key, expire)

async def blacklist_all_user_tokens(user_id: str):
    """
    Blacklist all tokens associated with a specific user (global logout).
    """
    key = f"{USER_TOKENS_PREFIX}{user_id}"
    tokens = await redis_client.smembers(key)
    for token in tokens:
        await set_blacklisted_token(token)
    await redis_client.delete(key)
