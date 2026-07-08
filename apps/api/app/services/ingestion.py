"""Persists a NormalizedJob from any connector into the shared `jobs` table
(deduped) and fans it out into a per-user `UserJob` row for every active
user, so each user's dashboard/queue reflects newly discovered postings.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ApplicationStatus
from app.models.job import Job, UserJob
from app.models.user import UserProfile
from app.services.job_sources.base import NormalizedJob
from app.services.job_sources.dedupe import compute_dedupe_hash


def upsert_job(session: Session, normalized: NormalizedJob) -> tuple[Job, bool]:
    existing = session.execute(
        select(Job).where(Job.source == normalized.source, Job.external_id == normalized.external_id)
    ).scalar_one_or_none()
    if existing:
        return existing, False

    job = Job(
        source=normalized.source,
        external_id=normalized.external_id,
        dedupe_hash=compute_dedupe_hash(normalized.title, normalized.company, normalized.location),
        title=normalized.title,
        company=normalized.company,
        company_logo_url=normalized.company_logo_url,
        location=normalized.location,
        workplace_type=normalized.workplace_type,
        employment_type=normalized.employment_type,
        experience_level=None,
        is_stem_opt_friendly=None,
        is_us_based=normalized.is_us_based,
        description=normalized.description,
        requirements=normalized.requirements,
        preferred_qualifications=normalized.preferred_qualifications,
        salary_range=normalized.salary_range,
        apply_url=normalized.apply_url,
        supports_auto_apply=normalized.supports_auto_apply,
        posted_at=normalized.posted_at,
        discovered_at=datetime.now(timezone.utc),
        raw_data=normalized.raw_data,
    )
    session.add(job)
    session.flush()
    return job, True


def is_duplicate_of_existing(session: Session, normalized: NormalizedJob) -> bool:
    """Catches the same posting mirrored across boards (e.g. a Greenhouse
    listing also copy-pasted onto the company's own career page) even
    though `source`/`external_id` differ.
    """
    dedupe_hash = compute_dedupe_hash(normalized.title, normalized.company, normalized.location)
    return (
        session.execute(select(Job.id).where(Job.dedupe_hash == dedupe_hash)).scalar_one_or_none()
        is not None
    )


def fan_out_to_users(session: Session, job: Job) -> list[UserJob]:
    user_ids = session.execute(select(UserProfile.id)).scalars().all()
    created: list[UserJob] = []
    for user_id in user_ids:
        existing = session.execute(
            select(UserJob).where(UserJob.user_id == user_id, UserJob.job_id == job.id)
        ).scalar_one_or_none()
        if existing:
            continue
        user_job = UserJob(user_id=user_id, job_id=job.id, status=ApplicationStatus.NEW)
        session.add(user_job)
        created.append(user_job)
    session.flush()
    return created
