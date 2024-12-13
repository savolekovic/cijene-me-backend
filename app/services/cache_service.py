from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from redis import asyncio as aioredis
from app.core.config import settings
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    @staticmethod
    async def clear_product_related_caches():
        """Clear all product-related caches"""
        if settings.USE_CACHE:
            logger.info("Clearing product-related caches")
            await FastAPICache.clear(namespace="products")
            await FastAPICache.clear(namespace="categories")
            await FastAPICache.clear(namespace="product_entries")

    @staticmethod
    async def clear_store_related_caches():
        """Clear all store-related caches"""
        if settings.USE_CACHE:
            logger.info("Clearing store-related caches")
            await FastAPICache.clear(namespace="store_brands")
            await FastAPICache.clear(namespace="store_locations")
            await FastAPICache.clear(namespace="product_entries")

    @staticmethod
    async def clear_user_related_caches():
        """Clear all user-related caches"""
        if settings.USE_CACHE:
            logger.info("Clearing user-related caches")
            await FastAPICache.clear(namespace="users")

async def init_cache():
    """Initialize Redis cache"""
    if settings.USE_CACHE:
        logger.info("Initializing cache")
        try:
            if settings.REDIS_URL:
                logger.info("Using Redis cache")
                redis = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf8",
                    decode_responses=True
                )
                FastAPICache.init(
                    RedisBackend(redis),
                    prefix=settings.CACHE_PREFIX
                )
                logger.info("Redis cache initialized successfully")
            else:
                # Fallback to in-memory cache if no Redis URL is provided
                logger.info("Redis URL not provided, using in-memory cache")
                FastAPICache.init(
                    InMemoryBackend(),
                    prefix=settings.CACHE_PREFIX
                )
                logger.info("In-memory cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {str(e)}")
            logger.info("Falling back to in-memory cache")
            FastAPICache.init(
                InMemoryBackend(),
                prefix=settings.CACHE_PREFIX
            )
    else:
        # Initialize with dummy backend when cache is disabled
        logger.info("Cache disabled, using dummy backend")
        class DummyBackend:
            async def get(self, key): return None
            async def set(self, key, value, expire=None): pass
            async def clear(self, namespace=None): pass
        
        FastAPICache.init(DummyBackend(), prefix=settings.CACHE_PREFIX) 