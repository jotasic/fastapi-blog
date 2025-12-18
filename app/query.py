from typing import TYPE_CHECKING

from sqlalchemy import select

from app.core.security import create_password_hash
from app.models import User

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.schemas import UserCreate


def get_user_by_email(*, session: Session, email) -> User | None:
    return session.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_user(*, session: Session, user_in: UserCreate) -> User:
    db_obj = User(**user_in.model_dump())
    db_obj.hashed_password = create_password_hash(user_in.password)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
