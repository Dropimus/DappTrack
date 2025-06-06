import redis.asyncio as redis
from config import get_settings

settings = get_settings()

REDIS_URL = settings.celery_broker_url

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    try:
        await redis_client.ping()  
        return redis_client
    except RedisError as e:
        raise RuntimeError(f"Redis connection error: {str(e)}")

async def close_redis():
    await redis_client.close()

