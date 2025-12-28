from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import create_random_post, create_random_user

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import Post


@pytest.fixture(scope="function")
async def sample_post(session: AsyncSession, default_user_token_header) -> Post:
    """
    테스트용 게시글 생성 (댓글을 달기 위해 필요)
    """

    user = await create_random_user(session)
    return await create_random_post(session, user)


@pytest.mark.anyio
async def test_write_comment(client: AsyncClient, default_user_token_header: dict[str, str], sample_post: Post):
    """
    인증된 사용자가 댓글을 작성하고, 생성된 댓글 정보를 반환받아야 합니다.
    """
    comment_data = {"comment": "This is a test comment", "short_id": sample_post.short_id}

    # URL 수정: /v1/comments -> /v1/post-comments
    response = await client.post("/v1/post-comments", json=comment_data, headers=default_user_token_header)

    assert response.status_code == 200
    created_comment = response.json()
    assert created_comment["comment"] == comment_data["comment"]
    assert "id" in created_comment


@pytest.mark.anyio
async def test_get_comments(client: AsyncClient, default_user_token_header: dict[str, str], sample_post: Post):
    """
    특정 게시글의 댓글 목록을 조회할 수 있어야 합니다.
    """
    # 1. 댓글 작성
    comment_data = [
        {"comment": "Comment 1", "short_id": sample_post.short_id},
        {"comment": "Comment 2", "short_id": sample_post.short_id},
        {"comment": "Comment 3", "short_id": sample_post.short_id},
        {"comment": "Comment 4", "short_id": sample_post.short_id},
    ]
    for comment in comment_data:
        await client.post("/v1/post-comments", json=comment, headers=default_user_token_header)

    # 2. 기본 조회 (short_id 사용) 및 기본 정렬 체크
    response = await client.get(f"/v1/post-comments?short_id={sample_post.short_id}")

    assert response.status_code == 200
    comments = response.json()
    assert comments[-1]["comment"] == comment_data[0]["comment"]

    # 3. 정렬 변경 체크
    response = await client.get(f"/v1/post-comments?short_id={sample_post.short_id}&order_direction=asc")

    assert response.status_code == 200
    comments = response.json()
    assert comments[0]["comment"] == comment_data[0]["comment"]

    # 4. 페이지네이션 체크
    response = await client.get(
        f"/v1/post-comments?short_id={sample_post.short_id}&order_direction=asc&limit=2&offset=2"
    )

    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2
    assert comments[0]["comment"] == comment_data[2]["comment"]


@pytest.mark.anyio
async def test_edit_comment(client: AsyncClient, default_user_token_header: dict[str, str], sample_post: Post):
    """
    자신의 댓글을 수정할 수 있어야 합니다.
    """
    # 1. 댓글 작성
    comment_data = {"comment": "Original Comment", "short_id": sample_post.short_id}
    response = await client.post("/v1/post-comments", json=comment_data, headers=default_user_token_header)
    created_comment = response.json()
    comment_id = created_comment["id"]

    # 2. 수정 요청
    edit_data = {"comment": "Updated Comment"}
    response = await client.patch(f"/v1/post-comments/{comment_id}", json=edit_data, headers=default_user_token_header)

    assert response.status_code == 200
    updated_comment = response.json()
    assert updated_comment["comment"] == "Updated Comment"


@pytest.mark.anyio
async def test_edit_comment_no_change(
    client: AsyncClient, default_user_token_header: dict[str, str], sample_post: Post
):
    """
    수정할 내용이 없으면 204 No Content를 반환해야 합니다.
    """
    # 1. 댓글 작성
    comment_data = {"comment": "Original Comment", "short_id": sample_post.short_id}
    response = await client.post("/v1/post-comments", json=comment_data, headers=default_user_token_header)
    comment_id = response.json()["id"]

    # 2. 빈 데이터로 수정 요청
    response = await client.patch(f"/v1/post-comments/{comment_id}", json={}, headers=default_user_token_header)

    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_comment(client: AsyncClient, default_user_token_header: dict[str, str], sample_post: Post):
    """
    자신의 댓글을 삭제할 수 있어야 합니다.
    """
    # 1. 댓글 작성
    comment_data = {"comment": "To be deleted", "short_id": sample_post.short_id}
    response = await client.post("/v1/post-comments", json=comment_data, headers=default_user_token_header)
    comment_id = response.json()["id"]

    # 2. 삭제 요청
    response = await client.delete(f"/v1/post-comments/{comment_id}", headers=default_user_token_header)
    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_other_user_comment(
    client: AsyncClient,
    default_user_token_header: dict[str, str],
    random_user_token_header: dict[str, str],
    sample_post: Post,
):
    """
    다른 사용자의 댓글을 삭제하려고 하면 403 에러가 발생해야 합니다.
    """
    # 1. default_user가 댓글 작성
    comment_data = {"comment": "My Comment", "short_id": sample_post.short_id}
    response = await client.post("/v1/post-comments", json=comment_data, headers=default_user_token_header)
    comment_id = response.json()["id"]

    # 2. other_user가 삭제 시도
    # URL 수정: /v1/comments -> /v1/post-comments
    response = await client.delete(f"/v1/post-comments/{comment_id}", headers=random_user_token_header)
    assert response.status_code == 403
