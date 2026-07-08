"""Lever Postings API — public, no auth required.
Docs: https://github.com/lever/postings-api
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import is_relevant_job

_BASE_URL = "https://api.lever.co/v0/postings/{company}"


class LeverConnector(JobSourceConnector):
    source = JobSourcePlatform.LEVER

    def __init__(self, company_slugs: list[str] | None = None) -> None:
        self._company_slugs = company_slugs or settings.lever_slugs_list

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for slug in self._company_slugs:
                try:
                    resp = await client.get(
                        _BASE_URL.format(company=slug), params={"mode": "json"}
                    )
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for job in resp.json():
                    title = job.get("text", "")
                    description = job.get("descriptionPlain") or job.get("description") or ""
                    if not is_relevant_job(title, description):
                        continue

                    categories = job.get("categories", {})
                    location = categories.get("location")
                    posted_at_ms = job.get("createdAt")
                    posted_at = (
                        datetime.fromtimestamp(posted_at_ms / 1000, tz=timezone.utc)
                        if posted_at_ms
                        else datetime.now(timezone.utc)
                    )

                    results.append(
                        NormalizedJob(
                            source=self.source,
                            external_id=job["id"],
                            title=title,
                            company=slug,
                            description=description,
                            apply_url=job.get("applyUrl") or job.get("hostedUrl", ""),
                            posted_at=posted_at,
                            location=location,
                            workplace_type=_map_commitment(categories.get("commitment")),
                            employment_type=EmploymentType.FULL_TIME,
                            is_us_based=_looks_us_based(location),
                            supports_auto_apply=True,
                            raw_data=job,
                        )
                    )
        return results


def _map_commitment(commitment: str | None) -> WorkplaceType | None:
    if not commitment:
        return None
    text = commitment.lower()
    if "remote" in text:
        return WorkplaceType.REMOTE
    if "hybrid" in text:
        return WorkplaceType.HYBRID
    return WorkplaceType.ONSITE


def _looks_us_based(location: str | None) -> bool:
    if not location:
        return True
    non_us_markers = ["india", "canada", "uk", "united kingdom", "germany", "poland"]
    return not any(marker in location.lower() for marker in non_us_markers)
