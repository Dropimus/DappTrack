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
    key = f"user:{user_id}:tracked_airdrops"
    await redis_client.delete(key)