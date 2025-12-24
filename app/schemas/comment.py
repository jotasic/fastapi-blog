from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, Field


class BasePostComment(BaseModel):
    comment: str | None = Field(default=None)
    is_delete: bool | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class PostCommentRead(BasePostComment):
    class Post(BaseModel):
        id: int
        short_id: str
        model_config = ConfigDict(from_attributes=True)

    class User(BaseModel):
        id: int
        nickname: str
        model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int | None = Field()
    user_id: int | None = Field()
    post: None | Post = Field()
    user: None | User = Field()

    model_config = ConfigDict(from_attributes=True)


class PostCommentCreate(BasePostComment):
    post_id: int = Field()
    user_id: int = Field()


class PostCommentWrite(BaseModel):
    comment: str = Field()
    short_id: str = Field(exclude=True)


class PostCommentEdit(BaseModel):
    comment: str | None = Field(default=None)
