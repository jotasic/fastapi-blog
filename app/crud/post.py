from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002
from sqlalchemy.orm import joinedload

from app.models import Post, User

if TYPE_CHECKING:
    from app.schemas import PostCreate
    from app.schemas.filters import PostFilterParams


async def get_post_list(*, session: AsyncSession, params: PostFilterParams) -> list[Post]:
    stmt = select(Post).join(User)

    conditions = []

    # 날짜 필터링 - 현재는 create_at으로 고정
    date_column = Post.created_at

    if params.start:
        conditions.append(date_column >= params.start)
    if params.end:
        conditions.append(date_column <= params.end)

    # 모든 조건을 and_ 로 묶어서 where 절에 한 번에 적용
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # 정렬 조건 - 현재는 created_at으로 고정
    order_by_column = Post.created_at
    order_by_option = order_by_column.desc() if params.order_direction == "desc" else order_by_column.asc()

    stmt = stmt.order_by(order_by_option).offset(params.offset).limit(params.limit).options(joinedload(Post.user))

    # 6. 쿼리를 실행하고 결과를 반환합니다.
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_post_by_short_id(session: AsyncSession, short_id: str) -> Post | None:
    stmt = select(Post).where(Post.short_id == short_id).options(joinedload(Post.user))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_post(session: AsyncSession, post_in: PostCreate):
    max_retries = 5
    for _ in range(max_retries):
        try:
            # 1. NanoID 생성 (12자)
            short_id = generate(size=12)

            # 2. Post 객체 생성
            db_obj = Post(**post_in.model_dump(), short_id=short_id)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

        except IntegrityError:
            await session.rollback()
            continue

    raise Exception("Failed to generate unique UID after multiple retries.")
