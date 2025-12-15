from typing import TYPE_CHECKING

from app.models import User
from tests.utils import random_email, random_lower_string

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


# TODO: 해당 테스트는 Test DB 셋업이 잘 되는지 확인하기 위함이므로 추후 실 Test 수정
def test_create_user(session: Session):
    name = random_lower_string(User.name.type.length)
    email = random_email()

    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    session.refresh(user)

    db_user = session.get(User, user.id)

    assert db_user.name == name
    assert db_user.email == email
