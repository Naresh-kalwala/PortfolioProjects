"""LinkedIn, Indeed, Dice, ZipRecruiter, and Wellfound do not offer a public,
ToS-compliant API for pulling individual job seekers' search results, and
their Terms of Service prohibit automated scraping or bot-driven
applications. Rather than skip these platforms, the app exposes an "Add Job"
action (dashboard button today, browser-extension/bookmarklet in a future
release) so the user pastes the job URL themselves — a manual, user-directed
action, not automated scraping.

Once pasted, the job re-enters the exact same pipeline as every connector
job: AI summary, match score, tailored resume, cover letter. It always lands
in "Manual Action Required" (`supports_auto_apply=False`) with a deep link
back to the original posting, because we never submit on these platforms
on the user's behalf.

If a user separately obtains an approved partner feed (e.g. an Indeed
Publisher/XML agreement), a real connector can be dropped in following the
same `JobSourceConnector` interface as greenhouse.py / lever.py without any
other code changes.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.enums import JobSourcePlatform
from app.services.job_sources.base import NormalizedJob

MANUAL_ASSIST_PLATFORMS = {
    JobSourcePlatform.LINKEDIN,
    JobSourcePlatform.INDEED,
    JobSourcePlatform.DICE,
    JobSourcePlatform.ZIPRECRUITER,
    JobSourcePlatform.WELLFOUND,
}


def build_job_from_manual_paste(
    *,
    source: JobSourcePlatform,
    url: str,
    title: str,
    company: str,
    description: str,
    location: str | None = None,
) -> NormalizedJob:
    if source not in MANUAL_ASSIST_PLATFORMS:
        raise ValueError(f"{source} is not a manual-assist platform")

    return NormalizedJob(
        source=source,
        external_id=url,
        title=title,
        company=company,
        description=description,
        apply_url=url,
        posted_at=datetime.now(timezone.utc),
        location=location,
        is_us_based=True,
        supports_auto_apply=False,
        raw_data={"ingested_via": "manual_paste"},
    )
