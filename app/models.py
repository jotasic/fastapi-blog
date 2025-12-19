from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, event, false, null
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func, true


class BaseModel(DeclarativeBase):
    def update_from_dict(self, data: dict[str, Any]):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(UTC), server_default=func.now(), index=True
    )


# 생성 시, create_at과 update_at에 동일한 값을 넣기 위한 작업
@event.listens_for(TimestampMixin, "before_insert", propagate=True)
def setup_default_timestamps(mapper, connection, target):
    current = datetime.now(UTC)
    if not target.created_at:
        target.created_at = current
        target.updated_at = current

    if not target.updated_at:
        target.updated_at = target.created_at


class SoftDeleteMixin:
    is_delete: Mapped[bool] = mapped_column(default=False, server_default=false())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, server_default=null())


class User(SoftDeleteMixin, TimestampMixin, BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(250))
    nickname: Mapped[str] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    posts: Mapped[list[Post]] = relationship(back_populates="user")


class Post(SoftDeleteMixin, TimestampMixin, BaseModel):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_id: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text())
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    user: Mapped[User] = relationship(back_populates="posts")
    comments: Mapped[list[PostComment]] = relationship(back_populates="posts")


class PostComment(SoftDeleteMixin, TimestampMixin, BaseModel):
    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(Text())

    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id", ondelete="SET NULL"), index=True)
    post: Mapped[Post] = relationship(back_populates="post_comments")

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    user: Mapped[User] = relationship(back_populates="post_comments")
