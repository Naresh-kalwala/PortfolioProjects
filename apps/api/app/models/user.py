from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.job import UserJob
    from app.models.resume import MasterResume, TailoredResume
    from app.models.cover_letter import CoverLetter
    from app.models.notification import Notification


class UserProfile(UUIDMixin, TimestampMixin, Base):
    """One row per authenticated user (mirrors the Clerk account)."""

    __tablename__ = "user_profiles"

    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Flexible structured data — kept as JSON to avoid premature normalization
    # while the schema for these sections is still evolving.
    work_history: Mapped[list] = mapped_column(JSON, default=list)
    education: Mapped[list] = mapped_column(JSON, default=list)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    preferred_locations: Mapped[list] = mapped_column(JSON, default=list)
    predefined_answers: Mapped[dict] = mapped_column(JSON, default=dict)

    salary_expectation_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_expectation_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(10), default="USD")

    work_authorization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    visa_status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requires_stem_opt: Mapped[bool] = mapped_column(default=False)

    # Safety gate: even on ATS platforms our automation can fill end-to-end,
    # the form is only ever auto-submitted without a human click if the user
    # has explicitly opted in here. Off by default.
    auto_submit_applications: Mapped[bool] = mapped_column(default=False)

    whatsapp_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notification_preferences: Mapped[dict] = mapped_column(
        JSON, default=lambda: {"email": True, "whatsapp": False, "browser_push": True}
    )
    push_subscriptions: Mapped[list] = mapped_column(JSON, default=list)

    master_resumes: Mapped[list["MasterResume"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    tailored_resumes: Mapped[list["TailoredResume"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    cover_letters: Mapped[list["CoverLetter"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    job_matches: Mapped[list["UserJob"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
