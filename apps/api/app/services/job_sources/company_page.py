"""Generic connector for individual company career pages that publish
schema.org JobPosting structured data (JSON-LD) — the standard search-engine
markup Google for Jobs relies on. This reads the same public, machine-
readable data search engines already index; it is not a headless-browser
scrape of rendered HTML or protected content.

Configure target pages via UserProfile/settings (a list of career page URLs
to poll) rather than a single global env var, since these are highly
company-specific.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.models.enums import EmploymentType, JobSourcePlatform, WorkplaceType
from app.services.job_sources.base import JobSourceConnector, NormalizedJob
from app.services.job_sources.target_roles import is_relevant_job


class CompanyPageConnector(JobSourceConnector):
    source = JobSourcePlatform.COMPANY_PAGE

    def __init__(self, career_page_urls: list[str]) -> None:
        self._urls = career_page_urls

    async def fetch_jobs(self, keywords: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            for url in self._urls:
                try:
                    resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; JobPlatformBot/1.0)"})
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for posting in _extract_job_postings(resp.text):
                    title = posting.get("title", "")
                    description = _strip_html(posting.get("description", ""))
                    if not is_relevant_job(title, description):
                        continue

                    results.append(
                        NormalizedJob(
                            source=self.source,
                            external_id=posting.get("identifier", {}).get("value") or title + url,
                            title=title,
                            company=(posting.get("hiringOrganization") or {}).get("name", ""),
                            description=description,
                            apply_url=posting.get("url") or url,
                            posted_at=_parse_datetime(posting.get("datePosted")),
                            location=_extract_location(posting),
                            workplace_type=WorkplaceType.REMOTE
                            if posting.get("jobLocationType") == "TELECOMMUTE"
                            else None,
                            employment_type=_map_employment_type(posting.get("employmentType")),
                            is_us_based=True,
                            supports_auto_apply=False,
                            raw_data=posting,
                        )
                    )
        return results


def _extract_job_postings(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    postings = []
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") == "JobPosting":
                postings.append(candidate)
    return postings


def _strip_html(text: str) -> str:
    return BeautifulSoup(text or "", "html.parser").get_text(separator="\n").strip()


def _extract_location(posting: dict) -> str | None:
    location = posting.get("jobLocation")
    if isinstance(location, list):
        location = location[0] if location else None
    if not isinstance(location, dict):
        return None
    address = location.get("address", {})
    parts = [address.get("addressLocality"), address.get("addressRegion")]
    return ", ".join(p for p in parts if p) or None


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def _map_employment_type(value: str | list | None) -> EmploymentType | None:
    if isinstance(value, list):
        value = value[0] if value else None
    if not value:
        return None
    mapping = {
        "FULL_TIME": EmploymentType.FULL_TIME,
        "PART_TIME": EmploymentType.PART_TIME,
        "CONTRACTOR": EmploymentType.CONTRACT,
        "INTERN": EmploymentType.INTERNSHIP,
    }
    return mapping.get(value.upper().replace(" ", "_"))
