from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.security import create_password_hash
from app.models.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas.user import UserCreate


async def get_user_by_email(*, session: AsyncSession, email) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(*, session: AsyncSession, user_in: UserCreate) -> User:
    db_obj = User(**user_in.model_dump())
    db_obj.hashed_password = create_password_hash(user_in.password)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj
