from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_profile
from app.db.session import get_db
from app.models.cover_letter import CoverLetter
from app.models.resume import MasterResume, TailoredResume
from app.models.user import UserProfile
from app.schemas.resume import CoverLetterRead, MasterResumeRead, TailoredResumeRead
from app.services.documents import extract_text_from_upload
from app.services.storage import get_storage_backend

router = APIRouter(tags=["resumes"])


@router.post("/resumes/master", response_model=MasterResumeRead, status_code=201)
async def upload_master_resume(
    file: UploadFile,
    name: str = "Master Resume",
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    raw_text = extract_text_from_upload(file.filename or "", content)
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from the uploaded file")

    file_type = (file.filename or "").split(".")[-1].lower()
    storage = get_storage_backend()
    file_key = f"master-resumes/{profile.id}/{file.filename}"
    await storage.upload(file_key, content, file.content_type or "application/octet-stream")

    await db.execute(
        update(MasterResume).where(MasterResume.user_id == profile.id).values(is_primary=False)
    )

    resume = MasterResume(
        user_id=profile.id,
        name=name,
        is_primary=True,
        raw_text=raw_text,
        original_file_key=file_key,
        original_file_type=file_type,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/resumes/master", response_model=list[MasterResumeRead])
async def list_master_resumes(
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MasterResume).where(MasterResume.user_id == profile.id).order_by(MasterResume.created_at.desc())
    )
    return result.scalars().all()


@router.get("/resumes/tailored/{tailored_resume_id}", response_model=TailoredResumeRead)
async def get_tailored_resume(
    tailored_resume_id: UUID,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TailoredResume).where(
            TailoredResume.id == tailored_resume_id, TailoredResume.user_id == profile.id
        )
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=404, detail="Tailored resume not found")
    return resume


@router.get("/resumes/tailored/{tailored_resume_id}/download")
async def download_tailored_resume(
    tailored_resume_id: UUID,
    file_format: str = "pdf",
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TailoredResume).where(
            TailoredResume.id == tailored_resume_id, TailoredResume.user_id == profile.id
        )
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=404, detail="Tailored resume not found")

    key = resume.pdf_file_key if file_format == "pdf" else resume.docx_file_key
    if not key:
        raise HTTPException(status_code=404, detail=f"No {file_format} file available yet")

    storage = get_storage_backend()
    signed_url = await storage.get_signed_url(key)
    return {"url": signed_url}


@router.get("/cover-letters/{cover_letter_id}", response_model=CoverLetterRead)
async def get_cover_letter(
    cover_letter_id: UUID,
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CoverLetter).where(CoverLetter.id == cover_letter_id, CoverLetter.user_id == profile.id)
    )
    letter = result.scalar_one_or_none()
    if letter is None:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return letter


@router.get("/cover-letters/{cover_letter_id}/download")
async def download_cover_letter(
    cover_letter_id: UUID,
    file_format: str = "pdf",
    profile: UserProfile = Depends(get_current_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CoverLetter).where(CoverLetter.id == cover_letter_id, CoverLetter.user_id == profile.id)
    )
    letter = result.scalar_one_or_none()
    if letter is None:
        raise HTTPException(status_code=404, detail="Cover letter not found")

    key = letter.pdf_file_key if file_format == "pdf" else letter.docx_file_key
    if not key:
        raise HTTPException(status_code=404, detail=f"No {file_format} file available yet")

    storage = get_storage_backend()
    signed_url = await storage.get_signed_url(key)
    return {"url": signed_url}
