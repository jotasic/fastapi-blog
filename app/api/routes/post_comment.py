from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from app import crud
from app.api.deps import AsyncSessionDep, AuthUserDep  # noqa: TC001
from app.schemas import (
    PostCommentCreate,
    PostCommentEdit,
    PostCommentFilterParams,  # noqa: TC001
    PostCommentRead,
    PostCommentWrite,
)

router = APIRouter()


@router.get("", response_model=list[PostCommentRead])
async def get_post_comments_api(session: AsyncSessionDep, params: Annotated[PostCommentFilterParams, Query()]):
    db_objs = await crud.get_post_comments(session=session, params=params)
    return db_objs


# TODO: 리턴 스키마 정의
@router.post("")
async def write_post_comment(session: AsyncSessionDep, post_comment_write: PostCommentWrite, user: AuthUserDep):
    post = await crud.get_post_by_short_id(session=session, short_id=post_comment_write.short_id)
    comment_in = PostCommentCreate(**post_comment_write.model_dump(), user_id=user.id, post_id=post.id)
    db_obj = await crud.create_post_comment(session=session, comment_in=comment_in)
    return db_obj


# TODO: 리턴 스키마 정의
@router.patch("/{comment_id}")
async def edit_post_comment(
    session: AsyncSessionDep, comment_edit: PostCommentEdit, user: AuthUserDep, comment_id: int
):
    comment = await crud.get_post_comment_by_id(session=session, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # 작성자 본인 인지 확인
    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this post")

    # 1. 클라이언트가 보낸 데이터 중, 값이 설정된 필드만 추출
    update_data = comment_edit.model_dump(exclude_unset=True)

    # 2. 수정할 내용이 없으면 204 No Content 반환
    if not update_data:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # 3. 업데이트 진행
    comment.update_from_dict(update_data)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_post_comment(session: AsyncSessionDep, user: AuthUserDep, comment_id: int):
    comment = await crud.get_post_comment_by_id(session=session, comment_id=comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # 작성자 본인 인지 확인
    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this post")

    comment.is_delete = True
    comment.deleted_at = datetime.now(UTC)

    session.add(comment)
    await session.commit()
