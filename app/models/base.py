from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, event, false, func, null
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
