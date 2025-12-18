import re
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import PASSWORD_PATTERN

if TYPE_CHECKING:
    from datetime import datetime


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
