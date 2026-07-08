from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MasterResumeCreate(BaseModel):
    name: str = "Master Resume"
    is_primary: bool = True
    raw_text: str
    structured_content: dict = {}


class MasterResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_primary: bool
    raw_text: str
    structured_content: dict
    original_file_key: str | None = None
    original_file_type: str | None = None
    created_at: datetime
    updated_at: datetime


class TailoredResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    structured_content: dict
    keywords_added: list[str] = []
    ai_model_used: str | None = None
    pdf_file_key: str | None = None
    docx_file_key: str | None = None
    created_at: datetime


class CoverLetterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    content: str
    ai_model_used: str | None = None
    pdf_file_key: str | None = None
    docx_file_key: str | None = None
    created_at: datetime
