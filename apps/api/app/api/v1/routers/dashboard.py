from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_profile
from app.db.session import get_db
from app.models.enums import ApplicationStatus
from app.models.job import Job, UserJob
from app.models.user import UserProfile
from app.schemas.notification import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_24h = now - timedelta(hours=24)

    base = select(func.count(UserJob.id)).where(UserJob.user_id == profile.id)

    async def count(extra_where=None, join_job=False):
        query = base
        if join_job:
            query = select(func.count(UserJob.id)).select_from(UserJob).join(Job, UserJob.job_id == Job.id).where(
                UserJob.user_id == profile.id
            )
        if extra_where is not None:
            query = query.where(extra_where)
        result = await db.execute(query)
        return result.scalar_one()

    jobs_found_today = await count(Job.discovered_at >= today_start, join_job=True)
    jobs_last_24h = await count(Job.discovered_at >= last_24h, join_job=True)
    resumes_generated = await count(UserJob.tailored_resume_id.is_not(None))
    cover_letters_generated = await count(UserJob.cover_letter_id.is_not(None))
    applied = await count(UserJob.applied_at.is_not(None))
    manual_action_required = await count(UserJob.status == ApplicationStatus.MANUAL_ACTION_REQUIRED)
    submitted = await count(UserJob.status == ApplicationStatus.SUBMITTED)
    interviews = await count(UserJob.status == ApplicationStatus.INTERVIEW)
    rejections = await count(UserJob.status == ApplicationStatus.REJECTED)
    saved_jobs = await count(UserJob.is_saved.is_(True))
    favorites = await count(UserJob.is_favorite.is_(True))

    avg_result = await db.execute(
        select(func.avg(UserJob.match_score)).where(
            UserJob.user_id == profile.id, UserJob.match_score.is_not(None)
        )
    )
    average_match_score = avg_result.scalar_one()

    return DashboardStats(
        jobs_found_today=jobs_found_today,
        jobs_last_24h=jobs_last_24h,
        resumes_generated=resumes_generated,
        cover_letters_generated=cover_letters_generated,
        applied=applied,
        manual_action_required=manual_action_required,
        submitted=submitted,
        interviews=interviews,
        rejections=rejections,
        saved_jobs=saved_jobs,
        favorites=favorites,
        average_match_score=float(average_match_score) if average_match_score is not None else None,
    )
