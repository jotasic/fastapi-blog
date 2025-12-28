from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from app import crud
from app.api.deps import AsyncSessionDep, AuthUserDep  # noqa: TC001
from app.schemas import (
    PostCreate,
    PostEdit,
    PostFilterParams,
    PostRead,
    PostWrite,
)

router = APIRouter()


@router.get("", response_model=list[PostRead])
async def get_posts(session: AsyncSessionDep, post_filter_params: Annotated[PostFilterParams, Query()]):
    posts = await crud.get_post_list(session=session, params=post_filter_params)
    return posts


@router.get("/{short_id}", response_model=PostRead)
async def get_post(session: AsyncSessionDep, short_id: str):
    post = await crud.get_post_by_short_id(session=session, short_id=short_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return post


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def write_post(session: AsyncSessionDep, user: AuthUserDep, post_write: PostWrite):
    post_in = PostCreate(**post_write.model_dump(), user_id=user.id)
    post = await crud.create_post(
        session=session,
        post_in=post_in,
    )
    return post


@router.delete("/{short_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_post(session: AsyncSessionDep, user: AuthUserDep, short_id: str):
    post = await crud.get_post_by_short_id(session=session, short_id=short_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # 작성자 본인 인지 확인
    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

    await session.delete(post)
    await session.commit()


@router.patch("/{short_id}", response_model=PostRead)
async def edit_my_post(session: AsyncSessionDep, user: AuthUserDep, short_id: str, post_edit: PostEdit):
    post = await crud.get_post_by_short_id(session=session, short_id=short_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # 작성자 본인 인지 확인
    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this post")

    # 1. 클라이언트가 보낸 데이터 중, 값이 설정된 필드만 추출
    update_data = post_edit.model_dump(exclude_unset=True)

    # 2. 수정할 내용이 없으면 204 No Content 반환
    if not update_data:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # 3. 업데이트 진행
    post.update_from_dict(update_data)
    session.add(post)
    await session.commit()
    await session.refresh(post)

    return post
