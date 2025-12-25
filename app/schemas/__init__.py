from .auth import SendCodeRequest, VerificationCodeCreate, VerificationCodeRead, VerifyCodeRequest
from .comment import (
    BasePostComment,
    PostCommentCreate,
    PostCommentEdit,
    PostCommentRead,
    PostCommentWrite,
)
from .common import BearerAccessToken
from .filters import PostCommentFilterParams, PostFilterParams
from .post import BasePost, PostCreate, PostEdit, PostRead, PostWrite
from .user import UserBase, UserCreate, UserRead, UserRegister, UserUpdateMe

__all__ = [
    "BasePostComment",
    "PostCommentCreate",
    "PostCommentEdit",
    "PostCommentRead",
    "PostCommentWrite",
    "BearerAccessToken",
    "PostCommentFilterParams",
    "PostFilterParams",
    "BasePost",
    "PostCreate",
    "PostEdit",
    "PostRead",
    "PostWrite",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserRegister",
    "UserUpdateMe",
    "SendCodeRequest",
    "VerificationCodeCreate",
    "VerificationCodeRead",
    "VerifyCodeRequest",
]


# 순환참조 이슈로 인하여 아래와 같이 해결
# https://github.com/fastapi/sqlmodel/discussions/757#discussioncomment-13204884
PostRead.model_rebuild()
