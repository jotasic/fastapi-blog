from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.user import UserRead


class BasePost(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None)
    is_delete: bool = Field(default=False)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class PostRead(BasePost):
    short_id: str = Field()
    user_id: int = Field()
    user: UserRead = Field()


class PostCreate(BasePost):
    user_id: int = Field()


class PostWrite(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field()


class PostEdit(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None)
