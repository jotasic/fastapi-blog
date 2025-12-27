from typing import TYPE_CHECKING

import pytest
from fastapi import status

from app import crud
from app.schemas import VerificationCodeRead
from tests.conftest import DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.orm import Session


@pytest.mark.anyio
async def test_send_verification_code(session: Session, async_redis_client, client: AsyncClient) -> None:
    data = {
        "email": "xodn61@naver.com",
        "action": "signup",
    }

    result = await client.post("/v1/auth/send-code", json=data)
    assert result.status_code == status.HTTP_202_ACCEPTED
    code_in = VerificationCodeRead(**data)

    code = await crud.get_verification_code(async_redis_client, code_in)

    assert code


@pytest.mark.anyio
async def test_login_user(session: Session, client: AsyncClient) -> None:
    data = {
        "username": DEFAULT_USER_EMAIL,
        "password": DEFAULT_USER_PASSWORD,
    }

    result = await client.post("/v1/auth/login", data=data)

    result_data = result.json()

    assert result.status_code == status.HTTP_200_OK
    assert "access_token" in result_data
    assert result_data["access_token"]


@pytest.mark.anyio
async def test_login_user_incorrect_password(client: AsyncClient) -> None:
    data = {
        "username": DEFAULT_USER_EMAIL,
        "password": "incorrect",
    }

    result = await client.post("/v1/auth/login", data=data)

    assert result.status_code == status.HTTP_400_BAD_REQUEST
