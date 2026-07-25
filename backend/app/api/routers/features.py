"""
Roadmap, Projects, GitHub, Interview, Jobs, and Tracker routers.
"""
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.user import User
from app.models.chat import Roadmap, GitHubAnalysis, LearningProgress, InterviewSession
from app.schemas.schemas import (
    RoadmapCreate, RoadmapOut, RoadmapProgressUpdate,
    ProjectRecommendRequest,
    GitHubAnalysisRequest, GitHubAnalysisOut,
    LearningProgressCreate, LearningProgressOut,
    InterviewRequest, InterviewEvaluateRequest, InterviewSessionOut,
    JobMatchRequest,
)
from app.services.roadmap_service import generate_roadmap
from app.services.github_service import analyze_github_profile
from app.services.groq_service import groq_service
from app.api.routers.auth import get_current_user_dep

# ────────────────────────── ROADMAP ──────────────────────────
roadmap_router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@roadmap_router.post("/generate", response_model=RoadmapOut, status_code=201)
async def create_roadmap(
    data: RoadmapCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    skills = data.current_skills or current_user.skills or []
    roadmap_data = await generate_roadmap(data.goal, skills)

    roadmap = Roadmap(
        user_id=current_user.id,
        goal=data.goal,
        roadmap_data=roadmap_data,
        progress={},
    )
    db.add(roadmap)
    await db.flush()
    await db.refresh(roadmap)
    return RoadmapOut.model_validate(roadmap)


@roadmap_router.get("/", response_model=list[RoadmapOut])
async def list_roadmaps(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Roadmap).where(Roadmap.user_id == current_user.id).order_by(desc(Roadmap.created_at))
    )
    return [RoadmapOut.model_validate(r) for r in result.scalars().all()]


@roadmap_router.put("/{roadmap_id}/progress", response_model=RoadmapOut)
async def update_roadmap_progress(
    roadmap_id: uuid.UUID,
    update: RoadmapProgressUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Roadmap).where(Roadmap.id == roadmap_id, Roadmap.user_id == current_user.id)
    )
    roadmap = result.scalar_one_or_none()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    progress = dict(roadmap.progress or {})
    progress[update.node_id] = update.completed
    roadmap.progress = progress
    await db.flush()
    await db.refresh(roadmap)
    return RoadmapOut.model_validate(roadmap)


# ────────────────────────── PROJECTS ──────────────────────────
projects_router = APIRouter(prefix="/projects", tags=["projects"])

PROJECT_PROMPT = """You are a project mentor for CS students.
Generate 8 project ideas based on the student's profile.
Return JSON:
{{
  "projects": [
    {{
      "id": 1,
      "title": "Project Title",
      "description": "2-3 sentence description",
      "difficulty": "beginner|intermediate|advanced",
      "estimated_days": 14,
      "tech_stack": ["Tech1", "Tech2"],
      "learning_outcomes": ["Outcome 1", "Outcome 2"],
      "github_starter": "https://github.com/search?q=...",
      "tags": ["web", "ai", "backend"]
    }}
  ]
}}

Skills: {skills}
Interests: {interests}
Goal: {goal}
Time available: {time} hours/week"""


@projects_router.post("/recommend")
async def recommend_projects(
    data: ProjectRecommendRequest,
    current_user: User = Depends(get_current_user_dep),
):
    prompt = PROJECT_PROMPT.format(
        skills=", ".join(data.skills),
        interests=", ".join(data.interests or ["General"]),
        goal=data.goal or "Full Stack Developer",
        time=data.time_available_hours or 10,
    )
    try:
        response = await groq_service.chat_completion(
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
            temperature=0.6,
        )
        return json.loads(response)
    except Exception:
        return _mock_projects()


def _mock_projects():
    return {
        "projects": [
            {
                "id": 1,
                "title": "AI Resume Analyzer",
                "description": "Build a tool that analyzes resumes using NLP to extract skills and score ATS compatibility.",
                "difficulty": "intermediate",
                "estimated_days": 14,
                "tech_stack": ["Python", "FastAPI", "React", "Groq API"],
                "learning_outcomes": ["LLM API integration", "PDF parsing", "REST APIs"],
                "github_starter": "https://github.com/search?q=resume+analyzer+python",
                "tags": ["ai", "fullstack", "nlp"],
            },
            {
                "id": 2,
                "title": "Real-Time Chat Application",
                "description": "WebSocket-based chat app with rooms, authentication, and message history.",
                "difficulty": "intermediate",
                "estimated_days": 10,
                "tech_stack": ["Node.js", "Socket.io", "React", "MongoDB"],
                "learning_outcomes": ["WebSockets", "State management", "Database design"],
                "github_starter": "https://github.com/search?q=socket.io+chat+app",
                "tags": ["backend", "realtime", "fullstack"],
            },
            {
                "id": 3,
                "title": "Personal Finance Tracker",
                "description": "Track income and expenses with charts, categories, and monthly reports.",
                "difficulty": "beginner",
                "estimated_days": 7,
                "tech_stack": ["React", "Chart.js", "LocalStorage / Firebase"],
                "learning_outcomes": ["Data visualization", "CRUD operations", "State management"],
                "github_starter": "https://github.com/search?q=finance+tracker+react",
                "tags": ["frontend", "beginner-friendly"],
            },
        ]
    }


# ────────────────────────── GITHUB ──────────────────────────
github_router = APIRouter(prefix="/github", tags=["github"])


@github_router.post("/analyze", response_model=GitHubAnalysisOut, status_code=201)
async def analyze_github(
    data: GitHubAnalysisRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    analysis_data = await analyze_github_profile(data.github_username)
    if "error" in analysis_data:
        raise HTTPException(status_code=404, detail=analysis_data["error"])

    analysis = GitHubAnalysis(
        user_id=current_user.id,
        github_username=data.github_username,
        analysis_data=analysis_data,
    )
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)
    return GitHubAnalysisOut.model_validate(analysis)


@github_router.get("/history", response_model=list[GitHubAnalysisOut])
async def github_history(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GitHubAnalysis)
        .where(GitHubAnalysis.user_id == current_user.id)
        .order_by(desc(GitHubAnalysis.created_at))
        .limit(5)
    )
    return [GitHubAnalysisOut.model_validate(a) for a in result.scalars().all()]


# ────────────────────────── INTERVIEW ──────────────────────────
interview_router = APIRouter(prefix="/interview", tags=["interview"])

QUESTION_PROMPT = """Generate ONE interview question for topic: {topic}, difficulty: {difficulty}.
Return JSON: {{"question": "...", "type": "behavioral|technical|situational", "hints": ["hint1", "hint2"]}}"""

EVALUATE_PROMPT = """Evaluate this interview answer:
Question: {question}
Answer: {answer}

Return JSON:
{{
  "score": <0-100>,
  "confidence": <0-100>,
  "technical_accuracy": <0-100>,
  "communication": <0-100>,
  "grammar_score": <0-100>,
  "strengths": ["..."],
  "improvements": ["..."],
  "ideal_answer_points": ["..."],
  "overall_feedback": "2-3 sentences"
}}"""


@interview_router.post("/question", response_model=InterviewSessionOut, status_code=201)
async def get_interview_question(
    data: InterviewRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    try:
        response = await groq_service.chat_completion(
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": QUESTION_PROMPT.format(
                    topic=data.topic, difficulty=data.difficulty
                )},
            ],
            json_mode=True,
            temperature=0.7,
        )
        q_data = json.loads(response)
        question_text = q_data.get("question", f"Tell me about your experience with {data.topic}.")
    except Exception:
        question_text = f"Tell me about your experience with {data.topic}. What projects have you built?"

    session = InterviewSession(
        user_id=current_user.id,
        topic=data.topic,
        question=question_text,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return InterviewSessionOut.model_validate(session)


@interview_router.post("/evaluate", response_model=InterviewSessionOut)
async def evaluate_answer(
    data: InterviewEvaluateRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == data.session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    try:
        response = await groq_service.chat_completion(
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": EVALUATE_PROMPT.format(
                    question=session.question, answer=data.answer
                )},
            ],
            json_mode=True,
            temperature=0.3,
        )
        feedback = json.loads(response)
    except Exception:
        feedback = {"score": 70, "overall_feedback": "Good attempt! Keep practicing."}

    session.answer = data.answer
    session.feedback = feedback
    session.score = feedback.get("score", 70)
    await db.flush()
    await db.refresh(session)
    return InterviewSessionOut.model_validate(session)


@interview_router.get("/history", response_model=list[InterviewSessionOut])
async def interview_history(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(desc(InterviewSession.created_at))
        .limit(20)
    )
    return [InterviewSessionOut.model_validate(s) for s in result.scalars().all()]


# ────────────────────────── TRACKER ──────────────────────────
tracker_router = APIRouter(prefix="/tracker", tags=["tracker"])


@tracker_router.get("/", response_model=list[LearningProgressOut])
async def get_progress(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningProgress).where(LearningProgress.user_id == current_user.id)
    )
    return [LearningProgressOut.model_validate(p) for p in result.scalars().all()]


@tracker_router.post("/", response_model=LearningProgressOut, status_code=201)
async def add_skill(
    data: LearningProgressCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    progress = LearningProgress(
        user_id=current_user.id,
        skill_name=data.skill_name,
        category=data.category,
        progress_percent=data.progress_percent,
        status=data.status,
        notes=data.notes,
    )
    db.add(progress)
    await db.flush()
    await db.refresh(progress)
    return LearningProgressOut.model_validate(progress)


@tracker_router.put("/{progress_id}", response_model=LearningProgressOut)
async def update_skill_progress(
    progress_id: uuid.UUID,
    data: LearningProgressCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningProgress).where(
            LearningProgress.id == progress_id,
            LearningProgress.user_id == current_user.id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        raise HTTPException(status_code=404, detail="Skill not found")

    for field, value in data.model_dump().items():
        setattr(progress, field, value)
    await db.flush()
    await db.refresh(progress)
    return LearningProgressOut.model_validate(progress)


# ────────────────────────── JOBS ──────────────────────────
jobs_router = APIRouter(prefix="/jobs", tags=["jobs"])

JOB_PROMPT = """Generate 6 job role matches for a student with this profile:
Skills: {skills}
Location preference: {location}
Experience: {experience} years
Interests: {interests}

Return JSON:
{{
  "matches": [
    {{
      "id": 1,
      "title": "Job Title",
      "company_type": "Startup|Mid-size|Enterprise",
      "match_percent": 85,
      "salary_range": "₹6-10 LPA",
      "required_skills": ["skill1", "skill2"],
      "missing_skills": ["skill3"],
      "reasons": ["Reason 1"],
      "apply_platforms": ["LinkedIn", "Naukri"],
      "location": "Remote/Hybrid/Bangalore"
    }}
  ]
}}"""


@jobs_router.post("/match")
async def match_jobs(
    data: JobMatchRequest,
    current_user: User = Depends(get_current_user_dep),
):
    skills = data.skills or current_user.skills or []
    try:
        response = await groq_service.chat_completion(
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": JOB_PROMPT.format(
                    skills=", ".join(skills),
                    location=data.location or "Remote",
                    experience=data.experience_years or 0,
                    interests=", ".join(data.interests or ["Software Development"]),
                )},
            ],
            json_mode=True,
            temperature=0.5,
        )
        return json.loads(response)
    except Exception:
        return _mock_jobs()


def _mock_jobs():
    return {
        "matches": [
            {
                "id": 1,
                "title": "Junior Full Stack Developer",
                "company_type": "Startup",
                "match_percent": 82,
                "salary_range": "₹5-8 LPA",
                "required_skills": ["React", "Node.js", "MongoDB"],
                "missing_skills": ["Docker", "AWS"],
                "reasons": ["Strong frontend skills", "Good project portfolio"],
                "apply_platforms": ["LinkedIn", "AngelList", "Internshala"],
                "location": "Remote",
            },
            {
                "id": 2,
                "title": "Python Backend Developer",
                "company_type": "Mid-size",
                "match_percent": 75,
                "salary_range": "₹6-10 LPA",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "missing_skills": ["Redis", "Celery"],
                "reasons": ["Python proficiency", "API development skills"],
                "apply_platforms": ["LinkedIn", "Naukri"],
                "location": "Hybrid - Bangalore",
            },
        ]
    }
