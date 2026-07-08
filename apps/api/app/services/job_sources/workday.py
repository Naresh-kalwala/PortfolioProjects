"""Workday CXS API — the same JSON endpoint a company's public Workday
careers site calls from the browser to render its own job listings. This
queries the employer's own published data, not a third-party board, so it
does not touch LinkedIn/Indeed-style ToS restrictions. Still: respect
robots.txt and keep polling frequency reasonable per tenant.

WORKDAY_TENANTS env format: comma-separated "host|tenant|site" triples, e.g.
  "microsoft.wd1.myworkdayjobs.com|microsoft|Microsoft_Careers"
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import TARGET_ROLE_KEYWORDS, is_relevant_job


class WorkdayConnector(JobSourceConnector):
    source = JobSourcePlatform.WORKDAY

    def __init__(self, tenants: list[str] | None = None) -> None:
        self._tenants = tenants or [t.strip() for t in settings.workday_tenants.split(",") if t.strip()]

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20) as client:
            for tenant_config in self._tenants:
                try:
                    host, tenant, site = tenant_config.split("|")
                except ValueError:
                    continue

                url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
                for keyword in (keywords or TARGET_ROLE_KEYWORDS)[:5]:
                    try:
                        resp = await client.post(
                            url,
                            json={"limit": 20, "offset": 0, "searchText": keyword},
                            headers={"Content-Type": "application/json"},
                        )
                        resp.raise_for_status()
                    except httpx.HTTPError:
                        continue

                    for posting in resp.json().get("jobPostings", []):
                        title = posting.get("title", "")
                        if not is_relevant_job(title):
                            continue

                        external_path = posting.get("externalPath", "")
                        results.append(
                            NormalizedJob(
                                source=self.source,
                                external_id=external_path or title,
                                title=title,
                                company=tenant,
                                description=title,  # Workday's list endpoint omits full JD;
                                # detail is fetched lazily by the tailoring task via externalPath.
                                apply_url=f"https://{host}/{tenant}/{site}{external_path}",
                                posted_at=_parse_posted(posting.get("postedOn")),
                                location=posting.get("locationsText"),
                                workplace_type=_guess_workplace(posting.get("locationsText")),
                                employment_type=EmploymentType.FULL_TIME,
                                is_us_based=True,
                                supports_auto_apply=False,  # Workday apply flows vary too much
                                # per tenant (custom questionnaires, assessments) to auto-submit
                                # safely; treated as manual-assist until a tenant is verified.
                                raw_data=posting,
                            )
                        )
        return _dedupe_by_external_id(results)


def _parse_posted(text: str | None) -> datetime:
    # Workday returns relative strings like "Posted Today" / "Posted 3 Days Ago".
    now = datetime.now(timezone.utc)
    if not text:
        return now
    return now


def _guess_workplace(location_text: str | None) -> WorkplaceType | None:
    if not location_text:
        return None
    text = location_text.lower()
    if "remote" in text:
        return WorkplaceType.REMOTE
    return WorkplaceType.ONSITE


def _dedupe_by_external_id(jobs: list[NormalizedJob]) -> list[NormalizedJob]:
    seen: set[str] = set()
    unique: list[NormalizedJob] = []
    for job in jobs:
        if job.external_id in seen:
            continue
        seen.add(job.external_id)
        unique.append(job)
    return unique
