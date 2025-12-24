from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import true

from app.models.base import BaseModel, SoftDeleteMixin, TimestampMixin


class User(SoftDeleteMixin, TimestampMixin, BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(250))
    nickname: Mapped[str] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    posts: Mapped[list[Post]] = relationship(back_populates="user")
    comments: Mapped[list[PostComment]] = relationship(back_populates="user")


class Post(SoftDeleteMixin, TimestampMixin, BaseModel):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_id: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text())
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    user: Mapped[User] = relationship(back_populates="posts")
    comments: Mapped[list[PostComment]] = relationship(back_populates="post")


class PostComment(SoftDeleteMixin, TimestampMixin, BaseModel):
    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[str] = mapped_column(Text())

    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id", ondelete="SET NULL"), index=True)
    post: Mapped[Post] = relationship(back_populates="comments")

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    user: Mapped[User] = relationship(back_populates="comments")
