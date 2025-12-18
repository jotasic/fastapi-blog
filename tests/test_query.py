from typing import TYPE_CHECKING

from app import query
from app.models import User
from app.schemas import UserCreate
from tests.utils import DEFAULT_USER_EMAIL, random_email, random_lower_string

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def test_create_user(session: Session):
    nickname = random_lower_string(User.nickname.type.length)
    email = random_email()
    password = "Test1234!"

    user_in = UserCreate(nickname=nickname, email=email, password=password)

    user_db = query.create_user(session=session, user_in=user_in)

    assert user_in.nickname == user_db.nickname
    assert user_in.email == user_db.email


def test_get_user_by_email(session: Session):
    user = query.get_user_by_email(session=session, email=DEFAULT_USER_EMAIL)
    assert user
