import re
from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import PASSWORD_PATTERN


# 공통 속성을 위한 기본 모델
class UserBase(BaseModel):
    email: EmailStr = Field(max_length=320)
    nickname: str = Field(min_length=2, max_length=30)
    is_active: bool = Field(default=True)
    is_delete: bool = Field(default=False)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)


# 사용자 생성을 위한 모델 (예: 회원가입 시)
class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=320)
    nickname: str = Field(min_length=2, max_length=30)
    password: str = Field(pattern=re.compile(PASSWORD_PATTERN))


class UserCreate(UserBase):
    password: str = Field(exclude=True, pattern=re.compile(PASSWORD_PATTERN))


class UserUpdateMe(BaseModel):
    nickname: str | None = Field(default=None, min_length=2, max_length=30)


# DB에서 읽어온 사용자 정보를 위한 모델 (API 응답용)
class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # SQLAlchemy 모델을 Pydantic 모델로 변환


class BearerAccessToken(BaseModel):
    access_token: str
    token_type: str = Field(default="Bearer", frozen=True)


class BasePost(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    contents: str | None = Field(default=None)
    is_delete: bool = Field(default=False)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class PostRead(BasePost):
    nanoid: str = Field()
    user_id: int = Field()
    user: UserRead = Field()


class PostCreate(BasePost):
    user_id: int = Field()


class PostWrite(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    contents: str = Field()


class PostEdit(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    contents: str | None = Field(default=None)


class PostUpdate(BasePost):
    user_id: int | None = Field(default=None)
    nanoid: str | None = Field(default=None)
