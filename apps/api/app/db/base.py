import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def str_enum(enum_cls: type[enum.Enum]) -> SAEnum:
    """SQLAlchemy's `Enum` type binds/reads using the Python member's `.name`
    by default. Our enums are `str, Enum` subclasses whose `.value` (e.g.
    "greenhouse") is what the Alembic migration used for the Postgres enum
    labels and what the API/frontend exchange as JSON — so every enum
    column must use `.value`, not `.name`, or every read/write throws
    `invalid input value for enum ...`.
    """
    return SAEnum(enum_cls, values_callable=lambda obj: [e.value for e in obj])


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
