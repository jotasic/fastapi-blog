from typing import Annotated

import redis as redis_sync
import redis.asyncio as redis_async
from fastapi import Depends

from app.core.config import get_setting

settings = get_setting()

async_redis_client = redis_async.from_url(settings.CACHE_URI, decode_responses=True)
sync_redis_client = redis_sync.from_url(settings.CACHE_URI, decode_responses=True)


async def get_async_redis():
    return async_redis_client


def get_sync_redis():
    return sync_redis_client


RedisAsyncDep = Annotated[redis_async.Redis, Depends(get_async_redis)]
