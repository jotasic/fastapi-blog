from typing import TYPE_CHECKING

from fastapi import status

from tests.conftest import DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import Session


def test_login_user(session: Session, client: TestClient) -> None:
    data = {
        "username": DEFAULT_USER_EMAIL,
        "password": DEFAULT_USER_PASSWORD,
    }

    result = client.post("/v1/auth/login", data=data)

    result_data = result.json()

    assert result.status_code == status.HTTP_200_OK
    assert "access_token" in result_data
    assert result_data["access_token"]


def test_login_user_incorrect_password(client: TestClient) -> None:
    data = {
        "username": DEFAULT_USER_EMAIL,
        "password": "incorrect",
    }

    result = client.post("/v1/auth/login", data=data)

    assert result.status_code == status.HTTP_400_BAD_REQUEST
