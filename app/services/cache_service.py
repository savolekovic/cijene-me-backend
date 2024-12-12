from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.core.config import settings

async def init_cache():
    redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(
        RedisBackend(redis),
        prefix=settings.CACHE_PREFIX
    ) 