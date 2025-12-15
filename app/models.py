from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    pass


# https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html#mixing-in-columns
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)


class SoftDeleteMixin:
    is_delete: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(default=None, nullable=True)


class User(SoftDeleteMixin, TimestampMixin, BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(250), nullable=False)
    nickname: Mapped[str] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
