from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

# conftest.py에 공통 fixture가 정의되어 있으므로, 이 파일은 테스트 로직에만 집중합니다.


def test_write_post_unauthorized(client: TestClient):
    """
    인증되지 않은 사용자가 글 작성을 시도하면 401 에러가 발생해야 합니다.
    """
    response = client.post(
        "/v1/posts",
        json={"title": "Test Title", "content": "Test content", "slug": "test-title"},
    )
    assert response.status_code == 401


def test_write_and_get_post(client: TestClient, default_user_token_header: dict[str, str]):
    """
    인증된 사용자가 글을 작성하고, 해당 글을 성공적으로 조회할 수 있어야 합니다.
    """
    # 1. 글 작성
    post_data = {"title": "My First Post", "content": "Hello World!", "slug": "my-first-post"}
    response = client.post("/v1/posts", json=post_data, headers=default_user_token_header)

    assert response.status_code == 201
    created_post = response.json()
    assert created_post["title"] == post_data["title"]

    short_id = created_post["short_id"]

    # 2. 방금 작성한 글 조회
    response = client.get(f"/v1/posts/{short_id}", headers=default_user_token_header)
    assert response.status_code == 200
    retrieved_post = response.json()
    assert retrieved_post["title"] == post_data["title"]
    assert retrieved_post["short_id"] == short_id


def test_get_non_existent_post(client: TestClient, default_user_token_header: dict[str, str]):
    """
    존재하지 않는 게시글 조회 시 404 에러가 발생해야 합니다.
    """
    response = client.get("/v1/posts/non-existent-id", headers=default_user_token_header)
    assert response.status_code == 404


def test_get_post_list(client: TestClient):
    """
    게시글 목록을 필터링과 함께 성공적으로 조회해야 합니다.
    """
    # conftest.py의 init_test_data에서 샘플 데이터가 생성되었다고 가정
    response = client.get("/v1/posts")
    assert response.status_code == 200
    assert len(response.json()) > 0
    response.json()

    response = client.get("/v1/posts/?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_post(client: TestClient, default_user_token_header: dict[str, str], random_user_token_header):
    """
    - 자신의 글은 삭제할 수 있어야 합니다. (204)
    - 다른 사람의 글은 삭제할 수 없어야 합니다. (403)
    """
    # 1. 테스트용 글 생성
    post_data = {"title": "To Be Deleted", "content": "...", "slug": "to-be-deleted"}
    response = client.post("/v1/posts", json=post_data, headers=default_user_token_header)
    assert response.status_code == 201
    short_id = response.json()["short_id"]

    # 2. 다른 사용자가 삭제 시도 -> 실패 (403)
    response = client.delete(f"/v1/posts/{short_id}", headers=random_user_token_header)
    assert response.status_code == 403

    # 3. 작성자가 직접 삭제 -> 성공 (204)
    response = client.delete(f"/v1/posts/{short_id}", headers=default_user_token_header)
    assert response.status_code == 204

    # 4. 삭제된 글 조회 -> 실패 (404)
    response = client.get(f"/v1/posts/{short_id}", headers=default_user_token_header)
    assert response.status_code == 404


def test_edit_post(client: TestClient, default_user_token_header: dict[str, str], random_user_token_header):
    """
    - 자신의 글은 수정할 수 있어야 합니다.
    - 다른 사람의 글은 수정할 수 없어야 합니다. (403)
    """
    # 1. 테스트용 글 생성
    post_data = {"title": "Original Title", "content": "..."}
    response = client.post("/v1/posts", json=post_data, headers=default_user_token_header)
    assert response.status_code == 201
    short_id = response.json()["short_id"]

    # 2. 다른 사용자가 수정 시도 -> 실패 (403)
    edit_data = {"title": "Edited by Hacker"}
    response = client.patch(f"/v1/posts/{short_id}", json=edit_data, headers=random_user_token_header)
    assert response.status_code == 403

    # 3. 인증되지 않은 사용자가 시도 -> 실패 (401)
    edit_data = {"title": "Edited by Hacker"}
    response = client.patch(f"/v1/posts/{short_id}", json=edit_data)
    assert response.status_code == 401

    # 4. 작성자가 직접 수정 -> 성공 (200)
    edit_data = {"title": "Updated Title"}
    response = client.patch(f"/v1/posts/{short_id}", json=edit_data, headers=default_user_token_header)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
