import asyncio
import logging

from sqlalchemy import select

from app.db.sync_session import SyncSessionLocal
from app.models.enums import ApplicationStatus
from app.models.job import Job, UserJob
from app.models.resume import MasterResume, TailoredResume
from app.models.cover_letter import CoverLetter
from app.models.user import UserProfile
from app.services.ai.cover_letter import generate_cover_letter
from app.services.ai.job_summarizer import summarize_job
from app.services.ai.match_score import compute_match_score
from app.services.ai.resume_tailor import tailor_resume
from app.services.documents import (
    render_cover_letter_docx,
    render_cover_letter_pdf,
    render_resume_docx,
    render_resume_pdf,
)
from app.services.storage import get_storage_backend
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

# Below this score we still show the job (so the user can see it exists)
# but skip spending AI calls tailoring a resume for a weak match.
MIN_MATCH_SCORE_TO_TAILOR = 50
HIGH_MATCH_NOTIFICATION_THRESHOLD = 80


@celery_app.task(name="app.tasks.resume_tasks.process_new_user_job")
def process_new_user_job(user_job_id: str) -> None:
    """Runs the full AI pipeline for one (user, job) pair: summarize, score,
    tailor resume, generate cover letter, then hand off to the application
    task to decide auto-apply vs. manual-action-required.
    """
    with SyncSessionLocal() as session:
        user_job = session.get(UserJob, user_job_id)
        if user_job is None:
            return

        job = session.get(Job, user_job.job_id)
        user = session.get(UserProfile, user_job.user_id)
        master_resume = session.execute(
            select(MasterResume).where(
                MasterResume.user_id == user.id, MasterResume.is_primary.is_(True)
            )
        ).scalar_one_or_none()

        if master_resume is None:
            logger.info("User %s has no master resume yet; skipping tailoring", user.id)
            return

        summary = asyncio.run(summarize_job(job.title, job.company, job.description))
        match_result = asyncio.run(
            compute_match_score(
                master_resume.raw_text, job.description, job.requirements, job.preferred_qualifications
            )
        )

        user_job.ai_summary = summary
        user_job.match_score = match_result.get("overall_score")
        user_job.match_breakdown = match_result.get("breakdown", {})
        user_job.ai_match_explanation = match_result.get("explanation")
        user_job.missing_skills = match_result.get("missing_skills", [])
        user_job.resume_improvement_suggestions = match_result.get(
            "resume_improvement_suggestions", []
        )
        user_job.status = ApplicationStatus.SUMMARIZED
        session.commit()

        if (user_job.match_score or 0) >= HIGH_MATCH_NOTIFICATION_THRESHOLD:
            from app.tasks.notification_tasks import notify_high_match_job

            notify_high_match_job.delay(str(user.id), str(job.id), user_job.match_score)

        if (user_job.match_score or 0) < MIN_MATCH_SCORE_TO_TAILOR:
            return

        tailored = asyncio.run(
            tailor_resume(master_resume.raw_text, job.title, job.company, job.description)
        )
        storage = get_storage_backend()
        contact_line = " | ".join(filter(None, [user.email, user.phone, user.linkedin_url]))

        pdf_bytes = render_resume_pdf(tailored, user.full_name or "Candidate", contact_line)
        docx_bytes = render_resume_docx(tailored, user.full_name or "Candidate", contact_line)
        pdf_key = f"resumes/{user.id}/{job.id}.pdf"
        docx_key = f"resumes/{user.id}/{job.id}.docx"
        asyncio.run(storage.upload(pdf_key, pdf_bytes, "application/pdf"))
        asyncio.run(
            storage.upload(
                docx_key, docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        )

        tailored_resume = TailoredResume(
            user_id=user.id,
            master_resume_id=master_resume.id,
            job_id=job.id,
            structured_content=tailored,
            keywords_added=tailored.get("keywords_added", []),
            ai_model_used=None,
            pdf_file_key=pdf_key,
            docx_file_key=docx_key,
        )
        session.add(tailored_resume)
        session.flush()

        letter_text = asyncio.run(
            generate_cover_letter(master_resume.raw_text, user.full_name or "", job.company, job.title, job.description)
        )
        letter_pdf = render_cover_letter_pdf(letter_text)
        letter_docx = render_cover_letter_docx(letter_text)
        letter_pdf_key = f"cover-letters/{user.id}/{job.id}.pdf"
        letter_docx_key = f"cover-letters/{user.id}/{job.id}.docx"
        asyncio.run(storage.upload(letter_pdf_key, letter_pdf, "application/pdf"))
        asyncio.run(
            storage.upload(
                letter_docx_key, letter_docx,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        )

        cover_letter = CoverLetter(
            user_id=user.id,
            job_id=job.id,
            content=letter_text,
            pdf_file_key=letter_pdf_key,
            docx_file_key=letter_docx_key,
        )
        session.add(cover_letter)
        session.flush()

        user_job.tailored_resume_id = tailored_resume.id
        user_job.cover_letter_id = cover_letter.id
        user_job.status = ApplicationStatus.COVER_LETTER_GENERATED
        session.commit()

        from app.tasks.application_tasks import process_application
        from app.tasks.notification_tasks import notify_resume_ready

        notify_resume_ready.delay(str(user.id), str(job.id))
        process_application.delay(str(user_job.id))
