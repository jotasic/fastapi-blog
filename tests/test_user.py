from typing import TYPE_CHECKING

import pytest
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import crud
from app.core.security import verify_password
from app.models import User
from app.schemas import VerificationCodeCreate
from tests.utils import DEFAULT_USER_EMAIL, DEFAULT_USER_NICKNAME, random_email, random_lower_string

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.orm import Session


@pytest.mark.anyio
async def test_register_user(session: Session, async_redis_client, client: AsyncClient) -> None:
    nickname = random_lower_string(User.nickname.type.length)
    email = random_email()
    password = "Test1234!"
    code = "123456"

    data = {"nickname": nickname, "email": email, "password": password, "verification_code": code}
    code_in = VerificationCodeCreate(email=email, action="signup", code=code)
    await crud.create_verification_code(async_redis_client, code_in)
    result = await client.post("/v1/user/register", json=data)

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


@pytest.mark.anyio
async def test_get_user_me(client: AsyncClient, default_user_token_header: dict[str, str]) -> None:
    result = await client.get("/v1/user/me", headers=default_user_token_header)
    current_user = result.json()

    assert result.status_code == status.HTTP_200_OK

    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_delete"] is False
    assert current_user["deleted_at"] is None
    assert current_user["email"] == DEFAULT_USER_EMAIL


@pytest.mark.anyio
async def test_get_user_me_without_token(client: AsyncClient) -> None:
    result = await client.get("/v1/user/me")
    assert result.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_update_user_me(session: Session, client: AsyncClient, default_user_token_header: dict[str, str]) -> None:
    data = {
        "nickname": "changed name",
    }

    result = await client.patch("/v1/user/me", headers=default_user_token_header, json=data)
    data = result.json()

    user = crud.get_user_by_email(session=session, email=DEFAULT_USER_EMAIL)

    assert result.status_code == status.HTTP_200_OK
    assert user.nickname == data["nickname"]


@pytest.mark.anyio
async def test_update_user_me_without_data(
    session: Session, client: AsyncClient, default_user_token_header: dict[str, str]
) -> None:
    data = {}
    result = await client.patch("/v1/user/me", headers=default_user_token_header, json=data)
    user = crud.get_user_by_email(session=session, email=DEFAULT_USER_EMAIL)
    assert result.status_code == status.HTTP_200_OK
    assert user.nickname == DEFAULT_USER_NICKNAME
