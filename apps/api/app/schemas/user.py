from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class WorkHistoryEntry(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str | None = None
    is_current: bool = False
    description: str
    achievements: list[str] = []


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class UserProfileBase(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    work_history: list[WorkHistoryEntry] = []
    education: list[EducationEntry] = []
    skills: list[str] = []
    certifications: list[str] = []
    preferred_locations: list[str] = []
    predefined_answers: dict[str, str] = {}
    salary_expectation_min: float | None = None
    salary_expectation_max: float | None = None
    salary_currency: str = "USD"
    work_authorization: str | None = None
    visa_status: str | None = None
    requires_stem_opt: bool = False
    auto_submit_applications: bool = False
    whatsapp_number: str | None = None
    notification_preferences: dict[str, bool] = {
        "email": True,
        "whatsapp": False,
        "browser_push": True,
    }


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    clerk_user_id: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
