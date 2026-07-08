"""Greenhouse Job Board API — public, no auth required, no ToS violation.
Docs: https://developers.greenhouse.io/job-board.html
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import is_relevant_job

_BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


class GreenhouseConnector(JobSourceConnector):
    source = JobSourcePlatform.GREENHOUSE

    def __init__(self, board_tokens: list[str] | None = None) -> None:
        self._board_tokens = board_tokens or settings.greenhouse_tokens_list

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for token in self._board_tokens:
                try:
                    resp = await client.get(
                        _BASE_URL.format(token=token), params={"content": "true"}
                    )
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for job in resp.json().get("jobs", []):
                    title = job.get("title", "")
                    content = job.get("content", "") or ""
                    if not is_relevant_job(title, content):
                        continue

                    location = (job.get("location") or {}).get("name")
                    posted_at = _parse_datetime(job.get("updated_at") or job.get("first_published"))

                    results.append(
                        NormalizedJob(
                            source=self.source,
                            external_id=str(job["id"]),
                            title=title,
                            company=token,
                            description=content,
                            apply_url=job.get("absolute_url", ""),
                            posted_at=posted_at,
                            location=location,
                            workplace_type=_guess_workplace_type(location, content),
                            employment_type=EmploymentType.FULL_TIME,
                            is_us_based=_looks_us_based(location),
                            supports_auto_apply=True,
                            raw_data=job,
                        )
                    )
        return results


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _guess_workplace_type(location: str | None, content: str) -> WorkplaceType | None:
    text = f"{location or ''} {content[:300]}".lower()
    if "remote" in text:
        return WorkplaceType.REMOTE
    if "hybrid" in text:
        return WorkplaceType.HYBRID
    if location:
        return WorkplaceType.ONSITE
    return None


def _looks_us_based(location: str | None) -> bool:
    if not location:
        return True
    non_us_markers = ["india", "canada", "uk", "united kingdom", "germany", "poland", "remote - emea"]
    return not any(marker in location.lower() for marker in non_us_markers)
