from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    ApplicationMethod,
    ApplicationStatus,
    EmploymentType,
    ExperienceLevel,
    JobSourcePlatform,
    WorkplaceType,
)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: JobSourcePlatform
    title: str
    company: str
    company_logo_url: str | None = None
    location: str | None = None
    workplace_type: WorkplaceType | None = None
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
    is_stem_opt_friendly: bool | None = None
    is_us_based: bool
    description: str
    requirements: list[str] = []
    preferred_qualifications: list[str] = []
    salary_range: str | None = None
    apply_url: str
    supports_auto_apply: bool
    posted_at: datetime
    discovered_at: datetime


class UserJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job: JobRead
    match_score: int | None = None
    match_breakdown: dict = {}
    ai_summary: str | None = None
    ai_match_explanation: str | None = None
    missing_skills: list[str] = []
    resume_improvement_suggestions: list[str] = []
    status: ApplicationStatus
    application_method: ApplicationMethod | None = None
    manual_action_reason: str | None = None
    manual_action_steps: list[str] = []
    resume_application_url: str | None = None
    is_saved: bool
    is_favorite: bool
    tailored_resume_id: UUID | None = None
    cover_letter_id: UUID | None = None
    applied_at: datetime | None = None
    submitted_at: datetime | None = None
    created_at: datetime


class JobFilterParams(BaseModel):
    workplace_type: WorkplaceType | None = None
    employment_type: EmploymentType | None = None
    experience_level: ExperienceLevel | None = None
    stem_opt_friendly: bool | None = None
    us_only: bool = True
    status: ApplicationStatus | None = None
    is_saved: bool | None = None
    is_favorite: bool | None = None
    search: str | None = None
    sort_by: str = "posted_at"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 25


class UserJobUpdate(BaseModel):
    is_saved: bool | None = None
    is_favorite: bool | None = None
    status: ApplicationStatus | None = None


class ManualJobCreate(BaseModel):
    """For LinkedIn/Indeed/Dice/ZipRecruiter/Wellfound: the user pastes a
    posting they found themselves (no scraping involved) and it re-enters
    the same AI pipeline as connector-sourced jobs.
    """

    source: JobSourcePlatform
    url: str
    title: str
    company: str
    description: str
    location: str | None = None
