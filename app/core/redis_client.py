from typing import Annotated

import redis as redis_sync
import redis.asyncio as redis_async
from fastapi import Depends

from app.core.config import settings

# Redis 사용시 아래내용 lifespan 에 추가
# async def lifespan():
#     client = await get_async_redis()
#     await client.ping()  # Optional: check connection
#     yield client
#     await client.aclose() # Optional: close connection when done

async_redis_client = redis_async.from_url(settings.CACHE_URI, decode_responses=True)
sync_redis_client = redis_sync.from_url(settings.CACHE_URI, decode_responses=True)


async def get_async_redis() -> redis_async.Redis:
    return async_redis_client


def get_sync_redis() -> redis_sync.Redis:
    return sync_redis_client


RedisAsyncDep = Annotated[redis_async.Redis, Depends(get_async_redis)]
