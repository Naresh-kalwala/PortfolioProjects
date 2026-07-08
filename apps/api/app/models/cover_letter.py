from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import UserProfile


class CoverLetter(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "cover_letters"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))

    content: Mapped[str] = mapped_column(Text)
    ai_model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pdf_file_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    docx_file_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    user: Mapped["UserProfile"] = relationship(back_populates="cover_letters")
