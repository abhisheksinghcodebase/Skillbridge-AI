"""
Phase 3 Routers: Portfolio Reviewer, Cover Letter Generator, LinkedIn Post Generator, and RAG Resume Q&A.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.api.routers.auth import get_current_user_dep
from app.services.portfolio_service import audit_portfolio_url
from app.services.rag_service import query_resume_with_rag
from app.services.groq_service import groq_service

router = APIRouter(prefix="/phase3", tags=["phase3"])


# ── Schemas ──────────────────────────────────────────

class PortfolioReviewRequest(BaseModel):
    portfolio_url: str


class CoverLetterRequest(BaseModel):
    target_role: str
    company_name: str
    job_description: Optional[str] = None


class LinkedInPostRequest(BaseModel):
    project_title: str
    tech_stack: List[str]
    key_features: Optional[str] = None


class RAGQueryRequest(BaseModel):
    question: str


# ── Endpoints ──────────────────────────────────────────

@router.post("/portfolio/review")
async def review_portfolio(
    data: PortfolioReviewRequest,
    current_user: User = Depends(get_current_user_dep),
):
    """Module 10: AI Portfolio Reviewer (UI, SEO, Responsiveness, Accessibility)."""
    return await audit_portfolio_url(data.portfolio_url)


@router.post("/tools/cover-letter")
async def generate_cover_letter(
    data: CoverLetterRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """Generate a tailored cover letter based on user profile & target job."""
    # Get user skills
    skills_str = ", ".join(current_user.skills) if current_user.skills else "Software Engineering"

    prompt = f"""Write a professional, compelling 3-paragraph Cover Letter for a student applying for:
Role: {data.target_role}
Company: {data.company_name}
Applicant Name: {current_user.name}
Key Skills: {skills_str}
Job Description Context: {data.job_description or 'Focus on enthusiasm, learning agility, and technical skills.'}

Make it engaging, non-generic, and highlight why the student is a great fit."""

    response = await groq_service.chat_completion(
        messages=[
            {"role": "system", "content": "You are an expert career writer. Write high-converting cover letters."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
    )
    return {"cover_letter": response}


@router.post("/tools/linkedin-post")
async def generate_linkedin_post(
    data: LinkedInPostRequest,
    current_user: User = Depends(get_current_user_dep),
):
    """Generate a viral, professional LinkedIn post showcasing a project."""
    prompt = f"""Write an engaging LinkedIn project showcase post for a developer:
Project Title: {data.project_title}
Tech Stack: {', '.join(data.tech_stack)}
Key Highlights: {data.key_features or 'Full stack implementation, responsive UI, clean architecture'}

Use relevant hashtags, line breaks for readability, and a call-to-action asking for feedback."""

    response = await groq_service.chat_completion(
        messages=[
            {"role": "system", "content": "You are a LinkedIn personal branding specialist for developers."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return {"linkedin_post": response}


@router.post("/resume/rag-chat")
async def rag_chat_resume(
    data: RAGQueryRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """Perform RAG search over the user's uploaded resume to answer specific questions."""
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id).order_by(desc(Resume.created_at)).limit(1)
    )
    resume = result.scalar_one_or_none()
    if not resume or not resume.raw_text:
        raise HTTPException(status_code=404, detail="Please upload a resume first to use RAG Q&A.")

    answer = await query_resume_with_rag(resume.raw_text, data.question)
    return {"question": data.question, "answer": answer}
