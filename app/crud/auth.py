from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redis.asyncio import Redis

    from app.schemas import VerificationCodeCreate, VerificationCodeRead


async def create_verification_code(cache: Redis, code_in: VerificationCodeCreate):
    await cache.setex(code_in.key, timedelta(minutes=5), code_in.code)


async def get_verification_code(cache: Redis, code_in: VerificationCodeRead) -> str | None:
    return await cache.get(code_in.key)
