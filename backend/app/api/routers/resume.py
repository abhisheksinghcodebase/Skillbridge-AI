"""
Resume router: upload, analyze, history using MongoDB.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorDatabase

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
    db: AsyncIOMotorDatabase = Depends(get_db),
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

    # Store in MongoDB
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
    await db.resumes.insert_one(resume.to_doc())
    return ResumeOut.model_validate(resume)


@router.get("/latest", response_model=ResumeOut)
async def get_latest_resume(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db.resumes.find_one(
        {"user_id": str(current_user.id)},
        sort=[("created_at", -1)]
    )
    if not doc:
        raise HTTPException(status_code=404, detail="No resume found")
    resume = Resume.from_doc(doc)
    return ResumeOut.model_validate(resume)


@router.get("/history", response_model=list[ResumeOut])
async def get_resume_history(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db.resumes.find(
        {"user_id": str(current_user.id)}
    ).sort("created_at", -1).limit(10)
    docs = [doc async for doc in cursor]
    return [ResumeOut.model_validate(Resume.from_doc(d)) for d in docs]
