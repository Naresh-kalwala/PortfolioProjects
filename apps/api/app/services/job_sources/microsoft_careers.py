"""Microsoft's own careers site search API (gcsservices.careers.microsoft.com),
the same endpoint careers.microsoft.com's frontend calls. Public, no auth.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import TARGET_ROLE_KEYWORDS, is_relevant_job

_SEARCH_URL = "https://gcsservices.careers.microsoft.com/search/api/v1/search"


class MicrosoftCareersConnector(JobSourceConnector):
    source = JobSourcePlatform.MICROSOFT_CAREERS

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for keyword in (keywords or TARGET_ROLE_KEYWORDS)[:6]:
                try:
                    resp = await client.get(
                        _SEARCH_URL,
                        params={
                            "q": keyword,
                            "l": "en_us",
                            "pg": 1,
                            "pgSz": 20,
                            "o": "Recent",
                            "flt": "true",
                        },
                    )
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for job in resp.json().get("operationResult", {}).get("result", {}).get("jobs", []):
                    title = job.get("title", "")
                    if not is_relevant_job(title):
                        continue

                    job_id = job.get("jobId")
                    properties = job.get("properties", {})
                    results.append(
                        NormalizedJob(
                            source=self.source,
                            external_id=str(job_id),
                            title=title,
                            company="Microsoft",
                            description=properties.get("description", "") or title,
                            apply_url=f"https://jobs.careers.microsoft.com/global/en/job/{job_id}",
                            posted_at=_parse_datetime(properties.get("postingDate")),
                            location=", ".join(
                                loc.get("description", "") for loc in job.get("primaryLocation", [])
                            )
                            if isinstance(job.get("primaryLocation"), list)
                            else job.get("primaryLocation", {}).get("description"),
                            workplace_type=_guess_workplace(properties.get("workSiteFlexibility")),
                            employment_type=EmploymentType.FULL_TIME,
                            is_us_based=True,
                            supports_auto_apply=False,
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


def _guess_workplace(flexibility: str | None) -> WorkplaceType | None:
    if not flexibility:
        return None
    text = flexibility.lower()
    if "remote" in text:
        return WorkplaceType.REMOTE
    if "hybrid" in text:
        return WorkplaceType.HYBRID
    return WorkplaceType.ONSITE
