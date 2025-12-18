from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, event, false, null
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func, true


class BaseModel(DeclarativeBase):
    def update_from_dict(self, data: dict[str, Any]):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )


# 생성 시, create_at과 update_at에 동일한 값을 넣기 위한 작업
# 각각 default=lambda: datetime.now(UTC) 설정 시, 각각 호출하므로 값이 미묘하게 달라짐
@event.listens_for(TimestampMixin, "before_insert", propagate=True)
def setup_default_timestamps(mapper, connection, target):
    print("setup_timestamps ca")
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
