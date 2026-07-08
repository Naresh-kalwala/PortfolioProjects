import asyncio
import logging

from app.db.sync_session import SyncSessionLocal
from app.models.enums import (
    AUTO_APPLY_CAPABLE_PLATFORMS,
    ApplicationMethod,
    ApplicationStatus,
)
from app.models.cover_letter import CoverLetter
from app.models.job import Job, UserJob
from app.models.resume import TailoredResume
from app.models.user import UserProfile
from app.services.automation.ats_auto_apply import attempt_auto_apply
from app.services.automation.base import ApplicantContext
from app.services.storage.download import download_to_temp_file
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.application_tasks.process_application")
def process_application(user_job_id: str) -> None:
    """Decides auto-apply vs. manual-action-required for one (user, job)
    pair, once its resume and cover letter are ready.
    """
    with SyncSessionLocal() as session:
        user_job = session.get(UserJob, user_job_id)
        if user_job is None:
            return

        job = session.get(Job, user_job.job_id)
        user = session.get(UserProfile, user_job.user_id)

        if not (job.supports_auto_apply and job.source in AUTO_APPLY_CAPABLE_PLATFORMS):
            _mark_manual_action_required(
                user_job,
                reason=(
                    f"{job.source.value.replace('_', ' ').title()} does not support automated "
                    "applications (either the platform's Terms of Service prohibit it, or this "
                    "posting's application form isn't structured enough to fill safely)."
                ),
                steps=[
                    "Open the application link",
                    "Sign in if required",
                    "Upload the tailored resume and cover letter already prepared for you",
                    "Answer any custom application questions",
                    "Submit the application",
                ],
                apply_url=job.apply_url,
            )
            session.commit()
            return

        tailored_resume = session.get(TailoredResume, user_job.tailored_resume_id)
        cover_letter = session.get(CoverLetter, user_job.cover_letter_id)

        try:
            resume_path = asyncio.run(download_to_temp_file(tailored_resume.pdf_file_key, ".pdf"))
            cover_letter_path = asyncio.run(download_to_temp_file(cover_letter.pdf_file_key, ".pdf"))
        except Exception:
            logger.exception("Failed to fetch generated documents for user_job %s", user_job_id)
            _mark_manual_action_required(
                user_job,
                reason="Could not retrieve the generated resume/cover letter for auto-fill.",
                steps=["Download your tailored resume and cover letter from the dashboard",
                       "Complete the application manually"],
                apply_url=job.apply_url,
            )
            session.commit()
            return

        applicant = ApplicantContext(
            full_name=user.full_name or "",
            email=user.email,
            phone=user.phone,
            linkedin_url=user.linkedin_url,
            portfolio_url=user.portfolio_url,
            github_url=user.github_url,
            resume_pdf_path=resume_path,
            cover_letter_pdf_path=cover_letter_path,
            predefined_answers=user.predefined_answers or {},
            work_authorization=user.work_authorization,
            visa_status=user.visa_status,
            requires_stem_opt=user.requires_stem_opt,
        )

        user_job.status = ApplicationStatus.AUTO_APPLYING
        session.commit()

        result = asyncio.run(
            attempt_auto_apply(job.apply_url, applicant, auto_submit=user.auto_submit_applications)
        )

        if result.submitted:
            from datetime import datetime, timezone

            user_job.status = ApplicationStatus.SUBMITTED
            user_job.application_method = ApplicationMethod.AUTO
            user_job.applied_at = datetime.now(timezone.utc)
            user_job.submitted_at = datetime.now(timezone.utc)
            session.commit()

            from app.tasks.notification_tasks import notify_application_submitted

            notify_application_submitted.delay(str(user.id), str(job.id))
        else:
            _mark_manual_action_required(
                user_job,
                reason=result.reason or "Automation could not complete this application safely.",
                steps=result.manual_action_steps or ["Complete the application manually"],
                apply_url=job.apply_url,
            )
            session.commit()

            from app.tasks.notification_tasks import notify_manual_action_required

            notify_manual_action_required.delay(str(user.id), str(job.id))


def _mark_manual_action_required(user_job: UserJob, reason: str, steps: list[str], apply_url: str) -> None:
    user_job.status = ApplicationStatus.MANUAL_ACTION_REQUIRED
    user_job.application_method = ApplicationMethod.MANUAL_ASSIST
    user_job.manual_action_reason = reason
    user_job.manual_action_steps = steps
    user_job.resume_application_url = apply_url
