from typing import Optional
import redis.asyncio as aioredis
import structlog
from app.core.config import settings

logger = structlog.get_logger()
redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> Optional[aioredis.Redis]:
    global redis_client
    if not settings.REDIS_URL:
        logger.info("REDIS_URL not configured. Redis support disabled.")
        redis_client = None
        return None

    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        return redis_client
    except Exception as exc:
        logger.warning("Failed to connect to Redis instance", error=str(exc))
        redis_client = None
        return None


async def close_redis():
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
        except Exception as exc:
            logger.warning("Error closing Redis client", error=str(exc))
        redis_client = None


async def get_redis() -> Optional[aioredis.Redis]:
    return redis_client
