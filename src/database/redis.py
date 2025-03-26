import redis.asyncio as r
from src.conf.config import settings

async def get_redis():
    redis = await r.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    try:
        yield redis
    finally:
        await redis.close()
