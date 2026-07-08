import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.db.sync_session import SyncSessionLocal
from app.services.ingestion import fan_out_to_users, is_duplicate_of_existing, upsert_job
from app.services.job_sources import ACTIVE_CONNECTORS
from app.services.job_sources.target_roles import TARGET_ROLE_KEYWORDS
from app.tasks.celery_app import celery_app
from app.tasks.resume_tasks import process_new_user_job

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.job_scan_tasks.scan_all_sources")
def scan_all_sources() -> dict:
    """Runs every JOB_SCAN_INTERVAL_MINUTES (default 30) via Celery beat.
    Fetches from every connector, drops anything older than
    JOB_MAX_AGE_HOURS, dedupes, stores, and fans new postings out to every
    user for AI processing.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.job_max_age_hours)
    total_fetched = 0
    total_new_jobs = 0
    total_new_user_jobs = 0

    with SyncSessionLocal() as session:
        for connector_cls in ACTIVE_CONNECTORS:
            connector = connector_cls()
            try:
                normalized_jobs = asyncio.run(connector.fetch_jobs(TARGET_ROLE_KEYWORDS))
            except Exception:
                logger.exception("Connector %s failed", connector_cls.__name__)
                continue

            total_fetched += len(normalized_jobs)

            for normalized in normalized_jobs:
                if normalized.posted_at < cutoff:
                    continue
                if is_duplicate_of_existing(session, normalized):
                    continue

                job, was_created = upsert_job(session, normalized)
                if was_created:
                    total_new_jobs += 1

                new_user_jobs = fan_out_to_users(session, job)
                total_new_user_jobs += len(new_user_jobs)
                session.commit()

                for user_job in new_user_jobs:
                    process_new_user_job.delay(str(user_job.id))

    logger.info(
        "Job scan complete: fetched=%s new_jobs=%s new_user_jobs=%s",
        total_fetched, total_new_jobs, total_new_user_jobs,
    )
    return {
        "fetched": total_fetched,
        "new_jobs": total_new_jobs,
        "new_user_jobs": total_new_user_jobs,
    }
