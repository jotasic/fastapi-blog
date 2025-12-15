from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    pass


# https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html#mixing-in-columns
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)


# TODO: 현재 해당 모델은 DB 테스트를 위한 임시 테이블로 user 기능 구현 시 수정 해야됨
class User(TimestampMixin, BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
