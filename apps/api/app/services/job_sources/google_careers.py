"""Google's own careers site search API (careers.google.com), the same
endpoint the public careers site calls. Public, no auth.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import TARGET_ROLE_KEYWORDS, is_relevant_job

_SEARCH_URL = "https://careers.google.com/api/v3/search/"


class GoogleCareersConnector(JobSourceConnector):
    source = JobSourcePlatform.GOOGLE_CAREERS

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for keyword in (keywords or TARGET_ROLE_KEYWORDS)[:6]:
                try:
                    resp = await client.get(
                        _SEARCH_URL,
                        params={"q": keyword, "location": "United States", "page": 1},
                    )
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for job in resp.json().get("jobs", []):
                    title = job.get("title", "")
                    description = job.get("summary", "") or ""
                    if not is_relevant_job(title, description):
                        continue

                    job_id = job.get("job_id") or job.get("id")
                    locations = job.get("locations", [])
                    location = locations[0].get("display") if locations else None

                    results.append(
                        NormalizedJob(
                            source=self.source,
                            external_id=str(job_id),
                            title=title,
                            company="Google",
                            description=description or title,
                            apply_url=job.get("apply_url")
                            or f"https://careers.google.com/jobs/results/{job_id}/",
                            posted_at=_parse_datetime(job.get("publish_date")),
                            location=location,
                            workplace_type=_guess_workplace(title, description),
                            employment_type=EmploymentType.FULL_TIME,
                            is_us_based=True,
                            supports_auto_apply=False,
                            raw_data=job,
                        )
                    )
        return results


def _parse_datetime(value: dict | str | None) -> datetime:
    if isinstance(value, dict) and all(k in value for k in ("year", "month", "day")):
        try:
            return datetime(value["year"], value["month"], value["day"], tzinfo=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)


def _guess_workplace(title: str, description: str) -> WorkplaceType | None:
    text = f"{title} {description}".lower()
    if "remote" in text:
        return WorkplaceType.REMOTE
    if "hybrid" in text:
        return WorkplaceType.HYBRID
    return None
