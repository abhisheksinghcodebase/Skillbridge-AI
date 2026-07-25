"""
Resume router: upload, analyze, history.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.schemas import ResumeOut
from app.services.resume_service import save_uploaded_file, extract_text_from_pdf, analyze_resume
from app.api.routers.auth import get_current_user_dep

router = APIRouter(prefix="/resume", tags=["resume"])

ALLOWED_TYPES = {"application/pdf", "application/octet-stream"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    # Validate file
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    # Save file
    file_path = await save_uploaded_file(content, file.filename)

    # Extract text
    raw_text = await extract_text_from_pdf(file_path)

    # AI Analysis
    analysis = await analyze_resume(raw_text)

    # Store in DB
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        raw_text=raw_text,
        resume_score=analysis.get("resume_score"),
        ats_score=analysis.get("ats_score"),
        strong_skills=analysis.get("strong_skills"),
        weak_skills=analysis.get("weak_skills"),
        grammar_issues=analysis.get("grammar_issues"),
        formatting_suggestions=analysis.get("formatting_suggestions"),
        missing_keywords=analysis.get("missing_keywords"),
        improvement_tips=analysis.get("improvement_tips"),
        experience_years=analysis.get("experience_years"),
        education=analysis.get("education"),
        projects_detected=analysis.get("projects_detected"),
        full_analysis=analysis,
    )
    db.add(resume)
    await db.flush()
    await db.refresh(resume)
    return ResumeOut.model_validate(resume)


@router.get("/latest", response_model=ResumeOut)
async def get_latest_resume(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(desc(Resume.created_at))
        .limit(1)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")
    return ResumeOut.model_validate(resume)


@router.get("/history", response_model=list[ResumeOut])
async def get_resume_history(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(desc(Resume.created_at))
        .limit(10)
    )
    return [ResumeOut.model_validate(r) for r in result.scalars().all()]
