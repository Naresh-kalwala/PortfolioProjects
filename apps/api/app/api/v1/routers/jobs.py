from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.v1.deps import get_current_profile
from app.db.session import get_db
from app.models.enums import ApplicationStatus, EmploymentType, ExperienceLevel, WorkplaceType
from app.models.job import Job, UserJob
from app.models.user import UserProfile
from app.schemas.job import ManualJobCreate, UserJobRead, UserJobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/manual", response_model=UserJobRead, status_code=201)
async def add_manual_job(
    payload: ManualJobCreate,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    """Adds a job the user found themselves on LinkedIn/Indeed/Dice/
    ZipRecruiter/Wellfound. These platforms are never auto-scraped or
    auto-applied to; this is a manual, user-initiated action that still
    gets the full AI treatment (summary, match score, tailored resume,
    cover letter) and always lands in Manual Action Required.
    """
    from app.db.sync_session import SyncSessionLocal
    from app.services.ingestion import fan_out_to_users, upsert_job
    from app.services.job_sources.manual_paste import build_job_from_manual_paste
    from app.tasks.resume_tasks import process_new_user_job

    normalized = build_job_from_manual_paste(
        source=payload.source,
        url=payload.url,
        title=payload.title,
        company=payload.company,
        description=payload.description,
        location=payload.location,
    )

    with SyncSessionLocal() as sync_session:
        job, _ = upsert_job(sync_session, normalized)
        new_user_jobs = fan_out_to_users(sync_session, job)
        sync_session.commit()
        job_id = job.id

    for user_job in new_user_jobs:
        process_new_user_job.delay(str(user_job.id))

    result = await db.execute(
        select(UserJob)
        .options(joinedload(UserJob.job))
        .where(UserJob.job_id == job_id, UserJob.user_id == profile.id)
    )
    user_job = result.unique().scalar_one_or_none()
    if user_job is None:
        # Race: this user's UserJob was created by fan_out_to_users above in
        # the same call, so it always exists; this branch is unreachable in
        # practice but keeps the endpoint's contract honest.
        raise HTTPException(status_code=500, detail="Failed to create job entry")
    return user_job


@router.get("", response_model=list[UserJobRead])
async def list_jobs(
    workplace_type: WorkplaceType | None = None,
    employment_type: EmploymentType | None = None,
    experience_level: ExperienceLevel | None = None,
    stem_opt_friendly: bool | None = None,
    us_only: bool = True,
    status: ApplicationStatus | None = None,
    is_saved: bool | None = None,
    is_favorite: bool | None = None,
    search: str | None = None,
    sort_by: str = Query("posted_at", pattern="^(posted_at|match_score|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(UserJob)
        .options(joinedload(UserJob.job))
        .join(Job, UserJob.job_id == Job.id)
        .where(UserJob.user_id == profile.id)
    )

    if workplace_type:
        query = query.where(Job.workplace_type == workplace_type)
    if employment_type:
        query = query.where(Job.employment_type == employment_type)
    if experience_level:
        query = query.where(Job.experience_level == experience_level)
    if stem_opt_friendly is not None:
        query = query.where(Job.is_stem_opt_friendly == stem_opt_friendly)
    if us_only:
        query = query.where(Job.is_us_based.is_(True))
    if status:
        query = query.where(UserJob.status == status)
    if is_saved is not None:
        query = query.where(UserJob.is_saved == is_saved)
    if is_favorite is not None:
        query = query.where(UserJob.is_favorite == is_favorite)
    if search:
        like_pattern = f"%{search}%"
        query = query.where(Job.title.ilike(like_pattern) | Job.company.ilike(like_pattern))

    sort_column = {
        "posted_at": Job.posted_at,
        "match_score": UserJob.match_score,
        "created_at": UserJob.created_at,
    }[sort_by]
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return result.unique().scalars().all()


@router.get("/{user_job_id}", response_model=UserJobRead)
async def get_job(
    user_job_id: UUID,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserJob)
        .options(joinedload(UserJob.job))
        .where(UserJob.id == user_job_id, UserJob.user_id == profile.id)
    )
    user_job = result.unique().scalar_one_or_none()
    if user_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return user_job


@router.patch("/{user_job_id}", response_model=UserJobRead)
async def update_job(
    user_job_id: UUID,
    payload: UserJobUpdate,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserJob)
        .options(joinedload(UserJob.job))
        .where(UserJob.id == user_job_id, UserJob.user_id == profile.id)
    )
    user_job = result.unique().scalar_one_or_none()
    if user_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user_job, field, value)

    await db.commit()
    await db.refresh(user_job)
    return user_job


@router.delete("/{user_job_id}", status_code=204)
async def delete_job(
    user_job_id: UUID,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    """Removes this job from the user's dashboard (e.g. one whose AI
    analysis failed and is stuck, or one they're no longer interested in).
    Only deletes this user's relationship to the posting — the shared `Job`
    row stays, so other users matched against it are unaffected, and
    re-adding the same posting later is still deduped correctly.
    """
    result = await db.execute(
        select(UserJob).where(UserJob.id == user_job_id, UserJob.user_id == profile.id)
    )
    user_job = result.scalar_one_or_none()
    if user_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    await db.delete(user_job)
    await db.commit()


@router.post("/{user_job_id}/resume-application", response_model=UserJobRead)
async def resume_application(
    user_job_id: UUID,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    """Called when the user clicks "Resume Application" after completing
    the manual steps themselves — marks the application submitted.
    """
    from datetime import datetime, timezone

    from app.models.enums import ApplicationMethod

    result = await db.execute(
        select(UserJob)
        .options(joinedload(UserJob.job))
        .where(UserJob.id == user_job_id, UserJob.user_id == profile.id)
    )
    user_job = result.unique().scalar_one_or_none()
    if user_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    user_job.status = ApplicationStatus.SUBMITTED
    user_job.application_method = ApplicationMethod.MANUAL_ASSIST
    user_job.submitted_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user_job)
    return user_job


@router.get("/{user_job_id}/interview-questions")
async def get_interview_questions(
    user_job_id: UUID,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    from app.services.ai.interview_prep import generate_interview_questions

    result = await db.execute(
        select(UserJob)
        .options(joinedload(UserJob.job))
        .where(UserJob.id == user_job_id, UserJob.user_id == profile.id)
    )
    user_job = result.unique().scalar_one_or_none()
    if user_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return await generate_interview_questions(user_job.job.title, user_job.job.description)


@router.post("/{user_job_id}/interview-answer")
async def get_interview_answer(
    user_job_id: UUID,
    question: str,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    from app.models.resume import MasterResume
    from app.services.ai.interview_prep import generate_interview_answer

    user_job_result = await db.execute(
        select(UserJob).where(UserJob.id == user_job_id, UserJob.user_id == profile.id)
    )
    if user_job_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_result = await db.execute(
        select(MasterResume).where(MasterResume.user_id == profile.id, MasterResume.is_primary.is_(True))
    )
    master_resume = resume_result.scalar_one_or_none()
    if master_resume is None:
        raise HTTPException(status_code=422, detail="Upload a master resume first")

    answer = await generate_interview_answer(master_resume.raw_text, question)
    return {"answer": answer}
