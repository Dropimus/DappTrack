import redis.asyncio as redis
from .config import get_settings

settings = get_settings()

REDIS_URL = settings.celery_broker_url

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def set_cache(key: str, value: str, expire: int = 3600):
    await redis_client.set(name=key, value=value, ex=expire)

async def get_cache(key: str) -> str | None:
    return await redis_client.get(key)

async def delete_cache(key: str):
    await redis_client.delete(key)

async def invalidate_tracked_airdrops_cache(user_id: str):
    # Invalidate all paginated tracked airdrops cache for this user
    pattern = f"user:{user_id}:tracked_airdrops*"
    async for key in redis_client.scan_iter(match=pattern):
        await redis_client.delete(key)

# --- Token Blacklisting for Session/Token Revocation ---

BLACKLIST_PREFIX = "blacklisted_token:"

async def set_blacklisted_token(token: str, expire: int = 60 * 60 * 24 * 7):
    """Blacklist a token for a week (default)."""
    await redis_client.set(f"{BLACKLIST_PREFIX}{token}", "1", ex=expire)

async def is_token_blacklisted(token: str) -> bool:
    return await redis_client.exists(f"{BLACKLIST_PREFIX}{token}") == 1