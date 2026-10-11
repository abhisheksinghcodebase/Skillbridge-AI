"""
Roadmap, Projects, GitHub, Interview, Jobs, and Tracker routers using MongoDB.
"""
from datetime import datetime
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

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
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    skills = data.current_skills or current_user.skills or []
    roadmap_data = await generate_roadmap(data.goal, skills)

    roadmap = Roadmap(
        user_id=current_user.id,
        goal=data.goal,
        roadmap_data=roadmap_data,
        progress={},
    )
    await db.roadmaps.insert_one(roadmap.to_doc())
    return RoadmapOut.model_validate(roadmap)


@roadmap_router.get("/", response_model=list[RoadmapOut])
async def list_roadmaps(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db.roadmaps.find({"user_id": str(current_user.id)}).sort("created_at", -1)
    docs = [doc async for doc in cursor]
    return [RoadmapOut.model_validate(Roadmap.from_doc(r)) for r in docs]


@roadmap_router.put("/{roadmap_id}/progress", response_model=RoadmapOut)
async def update_roadmap_progress(
    roadmap_id: uuid.UUID,
    update: RoadmapProgressUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db.roadmaps.find_one(
        {"id": str(roadmap_id), "user_id": str(current_user.id)}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    roadmap = Roadmap.from_doc(doc)
    progress = dict(roadmap.progress or {})
    progress[update.node_id] = update.completed
    roadmap.progress = progress
    roadmap.updated_at = datetime.utcnow()

    await db.roadmaps.update_one(
        {"id": str(roadmap_id)},
        {"$set": {"progress": progress, "updated_at": roadmap.updated_at}}
    )
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
                "title": "DevPortfolio CMS",
                "description": "A headless CMS for developer portfolios with markdown support and GitHub integration.",
                "difficulty": "beginner",
                "estimated_days": 7,
                "tech_stack": ["Next.js", "Tailwind CSS", "MongoDB"],
                "learning_outcomes": ["SSR/SSG", "Database modeling", "Auth"],
                "github_starter": "https://github.com/search?q=portfolio+cms+nextjs",
                "tags": ["web", "frontend", "fullstack"],
            },
            {
                "id": 3,
                "title": "Smart Job Application Tracker",
                "description": "Kanban board app to track job applications with salary insights and interview reminders.",
                "difficulty": "intermediate",
                "estimated_days": 10,
                "tech_stack": ["React", "FastAPI", "MongoDB"],
                "learning_outcomes": ["Drag and drop UI", "Relational design", "Email alerts"],
                "github_starter": "https://github.com/search?q=job+tracker+react",
                "tags": ["web", "productivity"],
            },
            {
                "id": 4,
                "title": "Real-time Coding Interview Platform",
                "description": "Collaborative code editor with WebRTC video calling and syntax highlighting.",
                "difficulty": "advanced",
                "estimated_days": 21,
                "tech_stack": ["Node.js", "WebSockets", "Monaco Editor", "Docker"],
                "learning_outcomes": ["WebSockets", "Sandboxed execution", "WebRTC"],
                "github_starter": "https://github.com/search?q=collaborative+editor+webrtc",
                "tags": ["advanced", "systems", "web"],
            },
            {
                "id": 5,
                "title": "GitHub Profile Readme Generator",
                "description": "Interactive CLI + Web tool to generate dynamic GitHub profile readmes with live stats.",
                "difficulty": "beginner",
                "estimated_days": 5,
                "tech_stack": ["TypeScript", "GitHub API", "Vercel"],
                "learning_outcomes": ["API consumption", "SVG generation", "Deployments"],
                "github_starter": "https://github.com/search?q=github+profile+readme+generator",
                "tags": ["tools", "open-source"],
            },
            {
                "id": 6,
                "title": "Distributed Task Queue",
                "description": "Lightweight Redis-backed background worker system in Python with retry logic.",
                "difficulty": "advanced",
                "estimated_days": 18,
                "tech_stack": ["Python", "Redis", "Asyncio"],
                "learning_outcomes": ["Concurrency", "Distributed systems", "Fault tolerance"],
                "github_starter": "https://github.com/search?q=python+task+queue",
                "tags": ["backend", "systems"],
            },
            {
                "id": 7,
                "title": "Algorithm Visualizer",
                "description": "Interactive visualizer for graph algorithms, dynamic programming, and sorting.",
                "difficulty": "intermediate",
                "estimated_days": 12,
                "tech_stack": ["React", "D3.js", "Tailwind CSS"],
                "learning_outcomes": ["Data structures", "D3 animations", "Complex state"],
                "github_starter": "https://github.com/search?q=algorithm+visualizer+react",
                "tags": ["dsa", "frontend", "education"],
            },
            {
                "id": 8,
                "title": "Microservices E-Commerce API",
                "description": "Event-driven backend with Auth, Catalog, Cart, and Order microservices.",
                "difficulty": "advanced",
                "estimated_days": 25,
                "tech_stack": ["FastAPI", "MongoDB", "RabbitMQ", "Docker"],
                "learning_outcomes": ["Microservices", "Event-driven architecture", "API Gateway"],
                "github_starter": "https://github.com/search?q=microservices+fastapi",
                "tags": ["backend", "cloud", "advanced"],
            },
        ]
    }


# ────────────────────────── GITHUB ──────────────────────────
github_router = APIRouter(prefix="/github", tags=["github"])


@github_router.post("/analyze", response_model=GitHubAnalysisOut, status_code=201)
async def analyze_github(
    data: GitHubAnalysisRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    analysis_data = await analyze_github_profile(data.github_username)
    if "error" in analysis_data:
        raise HTTPException(status_code=404, detail=analysis_data["error"])

    analysis = GitHubAnalysis(
        user_id=current_user.id,
        github_username=data.github_username,
        analysis_data=analysis_data,
    )
    await db.github_analyses.insert_one(analysis.to_doc())
    return GitHubAnalysisOut.model_validate(analysis)


@github_router.get("/history", response_model=list[GitHubAnalysisOut])
async def github_history(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db.github_analyses.find(
        {"user_id": str(current_user.id)}
    ).sort("created_at", -1).limit(5)
    docs = [doc async for doc in cursor]
    return [GitHubAnalysisOut.model_validate(GitHubAnalysis.from_doc(a)) for a in docs]


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
    db: AsyncIOMotorDatabase = Depends(get_db),
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
    await db.interview_sessions.insert_one(session.to_doc())
    return InterviewSessionOut.model_validate(session)


@interview_router.post("/evaluate", response_model=InterviewSessionOut)
async def evaluate_answer(
    data: InterviewEvaluateRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db.interview_sessions.find_one({
        "id": str(data.session_id),
        "user_id": str(current_user.id),
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Interview session not found")

    session = InterviewSession.from_doc(doc)

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

    await db.interview_sessions.update_one(
        {"id": str(data.session_id)},
        {"$set": {
            "answer": session.answer,
            "feedback": session.feedback,
            "score": session.score,
        }}
    )
    return InterviewSessionOut.model_validate(session)


@interview_router.get("/history", response_model=list[InterviewSessionOut])
async def interview_history(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db.interview_sessions.find(
        {"user_id": str(current_user.id)}
    ).sort("created_at", -1).limit(20)
    docs = [doc async for doc in cursor]
    return [InterviewSessionOut.model_validate(InterviewSession.from_doc(s)) for s in docs]


# ────────────────────────── TRACKER ──────────────────────────
tracker_router = APIRouter(prefix="/tracker", tags=["tracker"])


@tracker_router.get("/", response_model=list[LearningProgressOut])
async def get_progress(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db.learning_progress.find({"user_id": str(current_user.id)})
    docs = [doc async for doc in cursor]
    return [LearningProgressOut.model_validate(LearningProgress.from_doc(p)) for p in docs]


@tracker_router.post("/", response_model=LearningProgressOut, status_code=201)
async def add_skill(
    data: LearningProgressCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    progress = LearningProgress(
        user_id=current_user.id,
        skill_name=data.skill_name,
        category=data.category,
        progress_percent=data.progress_percent,
        status=data.status,
        notes=data.notes,
    )
    await db.learning_progress.insert_one(progress.to_doc())
    return LearningProgressOut.model_validate(progress)


@tracker_router.put("/{progress_id}", response_model=LearningProgressOut)
async def update_skill_progress(
    progress_id: uuid.UUID,
    data: LearningProgressCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db.learning_progress.find_one({
        "id": str(progress_id),
        "user_id": str(current_user.id),
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Skill not found")

    progress = LearningProgress.from_doc(doc)
    for field, value in data.model_dump().items():
        setattr(progress, field, value)
    progress.updated_at = datetime.utcnow()

    await db.learning_progress.update_one(
        {"id": str(progress_id)},
        {"$set": progress.to_doc()}
    )
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
                "required_skills": ["Python", "FastAPI", "MongoDB"],
                "missing_skills": ["Redis", "Celery"],
                "reasons": ["Python proficiency", "API development skills"],
                "apply_platforms": ["LinkedIn", "Naukri"],
                "location": "Hybrid - Bangalore",
            },
            {
                "id": 3,
                "title": "AI/ML Engineer Trainee",
                "company_type": "Enterprise",
                "match_percent": 70,
                "salary_range": "₹8-14 LPA",
                "required_skills": ["Python", "PyTorch", "NLP", "FastAPI"],
                "missing_skills": ["MLOps", "Kubernetes"],
                "reasons": ["AI interest aligned", "Strong foundation"],
                "apply_platforms": ["LinkedIn", "Company Portal"],
                "location": "Bangalore / Hyderabad",
            },
            {
                "id": 4,
                "title": "Frontend Engineer (React)",
                "company_type": "Startup",
                "match_percent": 88,
                "salary_range": "₹6-9 LPA",
                "required_skills": ["React", "TypeScript", "Tailwind CSS", "Next.js"],
                "missing_skills": ["GraphQL"],
                "reasons": ["High skill match on React & modern frontend stack"],
                "apply_platforms": ["Wellfound", "LinkedIn"],
                "location": "Remote",
            },
            {
                "id": 5,
                "title": "Associate Cloud / DevOps Engineer",
                "company_type": "Mid-size",
                "match_percent": 65,
                "salary_range": "₹5-7 LPA",
                "required_skills": ["Linux", "Docker", "Git", "CI/CD"],
                "missing_skills": ["Terraform", "Kubernetes"],
                "reasons": ["Good basics, high learning potential"],
                "apply_platforms": ["Naukri", "LinkedIn"],
                "location": "Pune / Gurgaon",
            },
            {
                "id": 6,
                "title": "Software Development Engineer (Fresher)",
                "company_type": "Enterprise",
                "match_percent": 78,
                "salary_range": "₹7-12 LPA",
                "required_skills": ["DSA", "Java or Python", "DBMS", "System Design Basics"],
                "missing_skills": ["System Design in depth"],
                "reasons": ["Solid CS fundamentals", "Good problem solving"],
                "apply_platforms": ["Campus / Off-campus portal"],
                "location": "PAN India",
            },
        ]
    }
