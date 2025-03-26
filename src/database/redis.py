import redis.asyncio as r

async def get_redis():
    redis = await r.Redis(host='localhost', port=6379, db=0)
    try:
        yield redis
    finally:
        await redis.close()
