from typing import TYPE_CHECKING

from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.crud import get_user_by_email
from app.models import User
from tests.utils import DEFAULT_USER_EMAIL, DEFAULT_USER_NICKNAME, random_email, random_lower_string

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import Session


def test_register_user(session: Session, client: TestClient) -> None:
    nickname = random_lower_string(User.nickname.type.length)
    email = random_email()
    password = "Test1234!"

    data = {
        "nickname": nickname,
        "email": email,
        "password": password,
    }

    result = client.post("/v1/user/register", json=data)

    created_user = result.json()
    assert result.status_code == status.HTTP_201_CREATED
    assert data["nickname"] == created_user["nickname"]
    assert data["email"] == created_user["email"]

    user_db = session.execute(select(User).where(User.email == email)).scalar_one_or_none()

    assert user_db
    assert user_db.email == email
    assert user_db.nickname == nickname
    assert user_db.created_at == user_db.updated_at
    assert verify_password(password, user_db.hashed_password)


def test_get_user_me(client: TestClient, default_user_token_header: dict[str, str]) -> None:
    result = client.get("/v1/user/me", headers=default_user_token_header)
    current_user = result.json()

    assert result.status_code == status.HTTP_200_OK

    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_delete"] is False
    assert current_user["deleted_at"] is None
    assert current_user["email"] == DEFAULT_USER_EMAIL


def test_get_user_me_without_token(client: TestClient) -> None:
    result = client.get("/v1/user/me")
    assert result.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_user_me(session: Session, client: TestClient, default_user_token_header: dict[str, str]) -> None:
    data = {
        "nickname": "changed name",
    }

    result = client.patch("/v1/user/me", headers=default_user_token_header, json=data)
    data = result.json()

    user = get_user_by_email(session=session, email=DEFAULT_USER_EMAIL)

    assert result.status_code == status.HTTP_200_OK
    assert user.nickname == data["nickname"]


def test_update_user_me_without_data(
    session: Session, client: TestClient, default_user_token_header: dict[str, str]
) -> None:
    data = {}
    result = client.patch("/v1/user/me", headers=default_user_token_header, json=data)
    user = get_user_by_email(session=session, email=DEFAULT_USER_EMAIL)
    assert result.status_code == status.HTTP_200_OK
    assert user.nickname == DEFAULT_USER_NICKNAME
