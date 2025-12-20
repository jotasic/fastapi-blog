from datetime import datetime  # noqa: TC003
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class PostFilterParams(BaseModel):
    limit: int = Field(default=20, gt=0, le=100, description="한 페이지에 표시할 게시글 수")
    offset: int = Field(default=0, ge=0, description="페이지 오프셋")
    order_by: Literal["created_at", "updated_at"] = Field(default="created_at", description="정렬 기준")
    order_direction: Literal["desc", "asc"] = Field(default="desc", description="정렬 방향")
    start: datetime | None = Field(default=None, description="조회 시작일")
    end: datetime | None = Field(default=None, description="조회 종료일")
    handle: str | None = Field(default=None, exclude=True, description="작성자 핸들(닉네임)으로 필터링")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start and self.end and self.start > self.end:
            raise ValueError("조회 시작일은 종료일보다 늦을 수 없습니다.")
        return self


class PostCommentFilterParams(BaseModel):
    post_short_id: str = Field(default=None, description="포스트 단축 id")
    limit: int = Field(default=20, gt=0, le=100, description="한 페이지에 표시할 댓글 수")
    offset: int = Field(default=0, ge=0, description="댓글 오프셋")
    order_by: Literal["created_at", "updated_at"] = Field(default="created_at", description="정렬 기준")
    order_direction: Literal["desc", "asc"] = Field(default="desc", description="정렬 방향")
