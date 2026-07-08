from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import UserProfile


class MasterResume(UUIDMixin, TimestampMixin, Base):
    """The single source-of-truth resume every tailored resume is derived
    from. A user may keep multiple named versions (e.g. "BI-focused",
    "Power Platform-focused") but exactly one is marked `is_primary`.
    """

    __tablename__ = "master_resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), default="Master Resume")
    is_primary: Mapped[bool] = mapped_column(default=True)

    # Structured content extracted from the uploaded file, used as the
    # factual ground truth the AI tailoring step is never allowed to
    # contradict or add to.
    structured_content: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_text: Mapped[str] = mapped_column(Text)

    original_file_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    original_file_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user: Mapped["UserProfile"] = relationship(back_populates="master_resumes")


class TailoredResume(UUIDMixin, TimestampMixin, Base):
    """An AI-tailored resume generated for one specific job, derived only
    from the master resume's factual content plus keyword/wording
    optimization — never fabricated experience or skills.
    """

    __tablename__ = "tailored_resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True
    )
    master_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("master_resumes.id", ondelete="CASCADE")
    )
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))

    structured_content: Mapped[dict] = mapped_column(JSON, default=dict)
    keywords_added: Mapped[list] = mapped_column(JSON, default=list)
    ai_model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pdf_file_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    docx_file_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    performance_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["UserProfile"] = relationship(back_populates="tailored_resumes")
