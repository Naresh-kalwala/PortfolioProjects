from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationChannel, NotificationType


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: NotificationType
    channel: NotificationChannel
    title: str
    body: str
    related_job_id: UUID | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    created_at: datetime


class DashboardStats(BaseModel):
    jobs_found_today: int
    jobs_last_24h: int
    resumes_generated: int
    cover_letters_generated: int
    applied: int
    manual_action_required: int
    submitted: int
    interviews: int
    rejections: int
    saved_jobs: int
    favorites: int
    average_match_score: float | None = None
