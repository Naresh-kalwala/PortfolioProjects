"""SmartRecruiters Posting API — public, no auth required.
Docs: https://developers.smartrecruiters.com/docs/job-postings-api
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import is_relevant_job

_LIST_URL = "https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
_DETAIL_URL = "https://api.smartrecruiters.com/v1/companies/{company_id}/postings/{posting_id}"


class SmartRecruitersConnector(JobSourceConnector):
    source = JobSourcePlatform.SMARTRECRUITERS

    def __init__(self, company_ids: list[str] | None = None) -> None:
        self._company_ids = company_ids or settings.smartrecruiters_ids_list

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for company_id in self._company_ids:
                try:
                    resp = await client.get(
                        _LIST_URL.format(company_id=company_id), params={"limit": 100}
                    )
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for job in resp.json().get("content", []):
                    title = job.get("name", "")
                    if not is_relevant_job(title):
                        continue

                    try:
                        detail_resp = await client.get(
                            _DETAIL_URL.format(company_id=company_id, posting_id=job["id"])
                        )
                        detail_resp.raise_for_status()
                        detail = detail_resp.json()
                    except httpx.HTTPError:
                        detail = {}

                    description = _extract_description(detail)
                    if not is_relevant_job(title, description):
                        continue

                    location = _format_location(job.get("location", {}))
                    posted_at = _parse_datetime(job.get("releasedDate"))

                    results.append(
                        NormalizedJob(
                            source=self.source,
                            external_id=str(job["id"]),
                            title=title,
                            company=job.get("company", {}).get("name", company_id),
                            description=description,
                            apply_url=job.get("ref", ""),
                            posted_at=posted_at,
                            location=location,
                            workplace_type=WorkplaceType.REMOTE
                            if job.get("location", {}).get("remote")
                            else None,
                            employment_type=EmploymentType.FULL_TIME,
                            is_us_based=_looks_us_based(job.get("location", {})),
                            supports_auto_apply=True,
                            raw_data=job,
                        )
                    )
        return results


def _extract_description(detail: dict) -> str:
    sections = (detail.get("jobAd") or {}).get("sections") or {}
    parts = []
    for section in sections.values():
        text = section.get("text")
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def _format_location(location: dict) -> str | None:
    if not location:
        return None
    parts = [location.get("city"), location.get("region"), location.get("country")]
    return ", ".join(p for p in parts if p)


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _looks_us_based(location: dict) -> bool:
    country = (location.get("country") or "").lower()
    return country in ("", "us", "usa", "united states")
