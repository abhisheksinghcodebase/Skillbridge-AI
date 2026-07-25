import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: uuid.UUID
    filename: str
    resume_score: Optional[float] = None
    ats_score: Optional[float] = None
    strong_skills: Optional[List[str]] = None
    weak_skills: Optional[List[str]] = None
    grammar_issues: Optional[List[str]] = None
    formatting_suggestions: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    improvement_tips: Optional[List[str]] = None
    experience_years: Optional[float] = None
    education: Optional[Dict[str, Any]] = None
    projects_detected: Optional[List[Any]] = None
    full_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[str] = None


class ChatMessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    session_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RoadmapCreate(BaseModel):
    goal: str
    current_skills: Optional[List[str]] = None


class RoadmapOut(BaseModel):
    id: uuid.UUID
    goal: str
    roadmap_data: Dict[str, Any]
    progress: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RoadmapProgressUpdate(BaseModel):
    node_id: str
    completed: bool


class ProjectRecommendRequest(BaseModel):
    skills: List[str]
    interests: Optional[List[str]] = None
    goal: Optional[str] = None
    time_available_hours: Optional[int] = None


class GitHubAnalysisRequest(BaseModel):
    github_username: str


class GitHubAnalysisOut(BaseModel):
    id: uuid.UUID
    github_username: str
    analysis_data: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningProgressCreate(BaseModel):
    skill_name: str
    category: Optional[str] = None
    progress_percent: int = 0
    status: str = "not_started"
    notes: Optional[str] = None


class LearningProgressOut(BaseModel):
    id: uuid.UUID
    skill_name: str
    category: Optional[str] = None
    progress_percent: int
    status: str
    notes: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class InterviewRequest(BaseModel):
    topic: str
    difficulty: Optional[str] = "medium"


class InterviewEvaluateRequest(BaseModel):
    session_id: uuid.UUID
    answer: str


class InterviewSessionOut(BaseModel):
    id: uuid.UUID
    topic: str
    question: str
    answer: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None
    score: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobMatchRequest(BaseModel):
    skills: List[str]
    location: Optional[str] = None
    experience_years: Optional[float] = None
    interests: Optional[List[str]] = None
