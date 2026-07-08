from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType


@dataclass
class NormalizedJob:
    """Common shape every connector maps its provider's response into,
    before it is deduped and persisted as a `Job` row."""

    source: JobSourcePlatform
    external_id: str
    title: str
    company: str
    description: str
    apply_url: str
    posted_at: datetime
    location: str | None = None
    company_logo_url: str | None = None
    workplace_type: WorkplaceType | None = None
    employment_type: EmploymentType | None = None
    salary_range: str | None = None
    requirements: list[str] = field(default_factory=list)
    preferred_qualifications: list[str] = field(default_factory=list)
    is_us_based: bool = True
    supports_auto_apply: bool = False
    raw_data: dict = field(default_factory=dict)


class JobSourceConnector(ABC):
    """A connector fetches postings from ONE platform via its official/public
    API. Connectors never use browser automation to scrape a job board's
    search results — only Playwright-driven *application* automation
    (separate service) touches a live browser session.
    """

    source: JobSourcePlatform

    @abstractmethod
    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        """Returns postings matching any of `keywords`, newest first."""
