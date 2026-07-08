from app.db.sync_session import SyncSessionLocal
from app.models.enums import NotificationType
from app.models.job import Job
from app.models.user import UserProfile
from app.services.notifications.dispatcher import dispatch_notification
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.notification_tasks.notify_high_match_job")
def notify_high_match_job(user_id: str, job_id: str, match_score: int) -> None:
    with SyncSessionLocal() as session:
        user = session.get(UserProfile, user_id)
        job = session.get(Job, job_id)
        dispatch_notification(
            session, user, NotificationType.HIGH_MATCH_JOB,
            title=f"{match_score}% match: {job.title} at {job.company}",
            body=f"A new high-match job was found: {job.title} at {job.company}.",
            related_job_id=job_id,
            url=job.apply_url,
        )


@celery_app.task(name="app.tasks.notification_tasks.notify_resume_ready")
def notify_resume_ready(user_id: str, job_id: str) -> None:
    with SyncSessionLocal() as session:
        user = session.get(UserProfile, user_id)
        job = session.get(Job, job_id)
        dispatch_notification(
            session, user, NotificationType.RESUME_READY,
            title=f"Resume & cover letter ready for {job.title}",
            body=f"Your tailored resume and cover letter for {job.title} at {job.company} are ready to review.",
            related_job_id=job_id,
        )


@celery_app.task(name="app.tasks.notification_tasks.notify_application_submitted")
def notify_application_submitted(user_id: str, job_id: str) -> None:
    with SyncSessionLocal() as session:
        user = session.get(UserProfile, user_id)
        job = session.get(Job, job_id)
        dispatch_notification(
            session, user, NotificationType.APPLICATION_SUBMITTED,
            title=f"Application submitted: {job.title}",
            body=f"Your application to {job.company} for {job.title} was submitted automatically.",
            related_job_id=job_id,
        )


@celery_app.task(name="app.tasks.notification_tasks.notify_manual_action_required")
def notify_manual_action_required(user_id: str, job_id: str) -> None:
    with SyncSessionLocal() as session:
        user = session.get(UserProfile, user_id)
        job = session.get(Job, job_id)
        dispatch_notification(
            session, user, NotificationType.MANUAL_ACTION_REQUIRED,
            title=f"Action needed: {job.title} at {job.company}",
            body="Everything is prepared — a few steps need your input to finish this application.",
            related_job_id=job_id,
            url=job.apply_url,
        )


@celery_app.task(name="app.tasks.notification_tasks.notify_interview_detected")
def notify_interview_detected(user_id: str, job_id: str) -> None:
    with SyncSessionLocal() as session:
        user = session.get(UserProfile, user_id)
        job = session.get(Job, job_id)
        dispatch_notification(
            session, user, NotificationType.INTERVIEW_DETECTED,
            title=f"Interview invitation detected: {job.title}",
            body=f"It looks like {job.company} wants to move forward with an interview for {job.title}.",
            related_job_id=job_id,
        )
