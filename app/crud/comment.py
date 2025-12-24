from typing import TYPE_CHECKING

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, contains_eager

from app.models import Post, PostComment, User

if TYPE_CHECKING:
    from app.schemas import PostCommentCreate, PostCommentRead
    from app.schemas.filters import PostCommentFilterParams


def get_post_comments(*, session: Session, params: PostCommentFilterParams) -> list[PostCommentRead]:
    stmt = select(PostComment).join(PostComment.user).join(PostComment.post)

    conditions = [PostComment.is_delete == False]  # noqa: E712

    if params.post_short_id:
        conditions.append(Post.short_id == params.post_short_id)

    # 모든 조건을 and_ 로 묶어서 where 절에 한 번에 적용
    if conditions:
        stmt = stmt.where(and_(*conditions))

    order_by_column = PostComment.created_at
    order_by_option = order_by_column.desc() if params.order_direction == "desc" else order_by_column.asc()

    # options 조인된 테이블의 특정 데이터만 가져오도록 옵션처리
    # post의 content의 경우 무거운 데이터가 될 수 있으므로 제외
    # contains_eager: 이미 조인되었으면 조인된 데이터를 활용
    # load_only : 조인시 해당되는 컬럼만 가져오기
    stmt = (
        stmt.order_by(order_by_option)
        .offset(params.offset)
        .limit(params.limit)
        .options(
            contains_eager(PostComment.user).load_only(User.id, User.nickname),
            contains_eager(PostComment.post).load_only(Post.id, Post.short_id),
        )
    )

    result = session.execute(stmt)
    return list(result.scalars().all())


def create_post_comment(*, session: Session, comment_in: PostCommentCreate):
    db_obj = PostComment(**comment_in.model_dump(exclude_unset=True))
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_post_comment_by_id(*, session: Session, comment_id: int):
    return session.execute(
        select(PostComment).where((PostComment.id == comment_id) & (PostComment.is_delete == False))  # noqa: E712, W291
    ).scalar_one_or_none()
