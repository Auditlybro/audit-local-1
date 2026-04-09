"""Redis connection."""
from redis.asyncio import Redis, from_url

from config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    """Get Redis connection (singleton)."""
    global _redis
    if _redis is None:
        _redis = from_url(
            settings.redis_url, 
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    return _redis


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
