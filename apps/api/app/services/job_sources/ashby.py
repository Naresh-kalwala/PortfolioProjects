"""Ashby Job Board API — public, no auth required.
Docs: https://developers.ashbyhq.com/reference/jobpostingsync-jobboard
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import is_relevant_job

_BASE_URL = "https://api.ashbyhq.com/posting-api/job-board/{board_name}"


class AshbyConnector(JobSourceConnector):
    source = JobSourcePlatform.ASHBY

    def __init__(self, board_names: list[str] | None = None) -> None:
        self._board_names = board_names or settings.ashby_boards_list

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for board_name in self._board_names:
                try:
                    resp = await client.get(
                        _BASE_URL.format(board_name=board_name),
                        params={"includeCompensation": "true"},
                    )
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for job in resp.json().get("jobs", []):
                    title = job.get("title", "")
                    description = job.get("descriptionPlain") or job.get("description") or ""
                    if not is_relevant_job(title, description):
                        continue

                    location = job.get("location")
                    posted_at = _parse_datetime(job.get("publishedAt"))

                    results.append(
                        NormalizedJob(
                            source=self.source,
                            external_id=job["id"],
                            title=title,
                            company=board_name,
                            description=description,
                            apply_url=job.get("applyUrl") or job.get("jobUrl", ""),
                            posted_at=posted_at,
                            location=location,
                            workplace_type=WorkplaceType.REMOTE if job.get("isRemote") else None,
                            employment_type=_map_employment_type(job.get("employmentType")),
                            salary_range=_format_compensation(job.get("compensation")),
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


def _map_employment_type(value: str | None) -> EmploymentType | None:
    if not value:
        return None
    mapping = {
        "FullTime": EmploymentType.FULL_TIME,
        "PartTime": EmploymentType.PART_TIME,
        "Contract": EmploymentType.CONTRACT,
        "Intern": EmploymentType.INTERNSHIP,
    }
    return mapping.get(value)


def _format_compensation(compensation: dict | None) -> str | None:
    if not compensation:
        return None
    summary = compensation.get("summaryComponents")
    if not summary:
        return None
    parts = [f"{c.get('minValue', '')}-{c.get('maxValue', '')} {c.get('currencyCode', '')}" for c in summary]
    return ", ".join(p for p in parts if p.strip("- "))


def _looks_us_based(location: str | None) -> bool:
    if not location:
        return True
    non_us_markers = ["india", "canada", "uk", "united kingdom", "germany", "poland"]
    return not any(marker in location.lower() for marker in non_us_markers)
