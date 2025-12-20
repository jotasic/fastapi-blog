from typing import TYPE_CHECKING

from nanoid import generate
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.core.security import create_password_hash
from app.models import Post, PostComment, User

if TYPE_CHECKING:
    from app.filters import PostCommentFilterParams, PostFilterParams
    from app.schemas import PostCommentCreate, PostCommentRead, PostCreate, UserCreate


def get_user_by_email(*, session: Session, email) -> User | None:
    return session.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_user(*, session: Session, user_in: UserCreate) -> User:
    db_obj = User(**user_in.model_dump())
    db_obj.hashed_password = create_password_hash(user_in.password)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_post_list(*, session: Session, params: PostFilterParams) -> list[Post]:
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
    result = session.execute(stmt)
    return list(result.scalars().all())


def get_post_by_short_id(session: Session, short_id: str) -> Post | None:
    stmt = select(Post).where(Post.short_id == short_id).options(joinedload(Post.user))
    db_obj = session.execute(stmt).scalar_one_or_none()
    return db_obj


def create_post(session: Session, post_in: PostCreate):
    max_retries = 5
    for _ in range(max_retries):
        try:
            # 1. NanoID 생성 (12자)
            short_id = generate(size=12)

            # 2. Post 객체 생성
            db_obj = Post(**post_in.model_dump(), short_id=short_id)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj

        except IntegrityError:
            session.rollback()
            continue

    raise Exception("Failed to generate unique UID after multiple retries.")


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
