import random
import string
from typing import TYPE_CHECKING

from app.core.security import create_password_hash
from app.models import User

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import Session


DEFAULT_USER_EMAIL = "example@test.com"
DEFAULT_USER_NICKNAME = "user"
DEFAULT_USER_PASSWORD = "Test1234!"


def random_lower_string(length: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def create_default_user(session: Session):
    user = User(
        nickname=DEFAULT_USER_NICKNAME,
        email=DEFAULT_USER_EMAIL,
        hashed_password=create_password_hash(DEFAULT_USER_PASSWORD),
    )
    session.add(user)
    session.commit()


def init_test_data(session: Session):
    create_default_user(session)


def get_user_token(*, client: TestClient, email: str, password: str) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post("/v1/auth/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers
