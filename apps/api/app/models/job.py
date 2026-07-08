from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin, str_enum
from app.models.enums import (
    ApplicationMethod,
    ApplicationStatus,
    EmploymentType,
    ExperienceLevel,
    JobSourcePlatform,
    WorkplaceType,
)

if TYPE_CHECKING:
    from app.models.user import UserProfile
    from app.models.resume import TailoredResume
    from app.models.cover_letter import CoverLetter


class Job(UUIDMixin, TimestampMixin, Base):
    """A job posting discovered from any source. Shared across all users
    (deduplicated), so the same posting is never re-fetched or re-stored
    twice regardless of how many users match against it.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),
    )

    source: Mapped[JobSourcePlatform] = mapped_column(str_enum(JobSourcePlatform), index=True)
    # Wide enough for a raw URL: manual-paste sources (LinkedIn, Indeed,
    # ...) use the posting's full URL as external_id, and those routinely
    # exceed 255 characters once tracking query params are included.
    external_id: Mapped[str] = mapped_column(String(2048), index=True)
    dedupe_hash: Mapped[str] = mapped_column(String(64), index=True)

    title: Mapped[str] = mapped_column(String(500))
    company: Mapped[str] = mapped_column(String(255), index=True)
    company_logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    workplace_type: Mapped[WorkplaceType | None] = mapped_column(str_enum(WorkplaceType), nullable=True)
    employment_type: Mapped[EmploymentType | None] = mapped_column(str_enum(EmploymentType), nullable=True)
    experience_level: Mapped[ExperienceLevel | None] = mapped_column(str_enum(ExperienceLevel), nullable=True)
    is_stem_opt_friendly: Mapped[bool | None] = mapped_column(nullable=True)
    is_us_based: Mapped[bool] = mapped_column(default=True)

    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[list] = mapped_column(JSON, default=list)
    preferred_qualifications: Mapped[list] = mapped_column(JSON, default=list)
    salary_range: Mapped[str | None] = mapped_column(String(255), nullable=True)

    apply_url: Mapped[str] = mapped_column(String(1000))
    # True only for platforms in AUTO_APPLY_CAPABLE_PLATFORMS with a
    # structured application form our automation can drive end-to-end.
    supports_auto_apply: Mapped[bool] = mapped_column(default=False)

    posted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), index=True)
    discovered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)

    user_matches: Mapped[list["UserJob"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class UserJob(UUIDMixin, TimestampMixin, Base):
    """Per-user relationship to a job: match score, AI analysis, generated
    documents, application progress. Kept separate from `Job` because the
    same posting can match many users differently.
    """

    __tablename__ = "user_jobs"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_job"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True
    )

    match_score: Mapped[int | None] = mapped_column(nullable=True)  # 0-100
    match_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_match_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    resume_improvement_suggestions: Mapped[list] = mapped_column(JSON, default=list)

    status: Mapped[ApplicationStatus] = mapped_column(
        str_enum(ApplicationStatus), default=ApplicationStatus.NEW, index=True
    )
    application_method: Mapped[ApplicationMethod | None] = mapped_column(
        str_enum(ApplicationMethod), nullable=True
    )
    manual_action_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    manual_action_steps: Mapped[list] = mapped_column(JSON, default=list)
    resume_application_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    is_saved: Mapped[bool] = mapped_column(default=False)
    is_favorite: Mapped[bool] = mapped_column(default=False)

    tailored_resume_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tailored_resumes.id", ondelete="SET NULL"), nullable=True
    )
    cover_letter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cover_letters.id", ondelete="SET NULL"), nullable=True
    )

    applied_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["UserProfile"] = relationship(back_populates="job_matches")
    job: Mapped["Job"] = relationship(back_populates="user_matches")
    tailored_resume: Mapped["TailoredResume | None"] = relationship()
    cover_letter: Mapped["CoverLetter | None"] = relationship()
