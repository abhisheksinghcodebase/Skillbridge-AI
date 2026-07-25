"""
SkillBridge AI — FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base

# Import all models so Alembic/SQLAlchemy can see them
from app.models import User, Resume, ChatMessage, Roadmap, GitHubAnalysis, LearningProgress, InterviewSession  # noqa

# Import routers
from app.api.routers.auth import router as auth_router
from app.api.routers.resume import router as resume_router
from app.api.routers.chat import router as chat_router
from app.api.routers.features import (
    roadmap_router,
    projects_router,
    github_router,
    interview_router,
    tracker_router,
    jobs_router,
)
from app.api.routers.phase3 import router as phase3_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create upload directory
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    # Create all tables (dev convenience — use Alembic for production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered career mentoring platform for students",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(resume_router, prefix=API_PREFIX)
app.include_router(chat_router, prefix=API_PREFIX)
app.include_router(roadmap_router, prefix=API_PREFIX)
app.include_router(projects_router, prefix=API_PREFIX)
app.include_router(github_router, prefix=API_PREFIX)
app.include_router(interview_router, prefix=API_PREFIX)
app.include_router(tracker_router, prefix=API_PREFIX)
app.include_router(jobs_router, prefix=API_PREFIX)
app.include_router(phase3_router, prefix=API_PREFIX)


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "groq_configured": bool(settings.GROQ_API_KEY),
    }


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API", "docs": "/api/docs"}
