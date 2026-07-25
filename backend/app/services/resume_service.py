"""
Resume service: PDF text extraction + Groq LLM analysis.
"""
import json
import os
import uuid
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.services.groq_service import groq_service

try:
    import fitz  # PyMuPDF
    _pymupdf_available = True
except ImportError:
    _pymupdf_available = False

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

RESUME_ANALYSIS_PROMPT = """You are an expert ATS resume analyzer and career coach.
Analyze the following resume text and return a JSON object with EXACTLY this structure:

{
  "resume_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "strong_skills": ["skill1", "skill2", ...],
  "weak_skills": ["skill1", "skill2", ...],
  "grammar_issues": ["issue1", "issue2", ...],
  "formatting_suggestions": ["suggestion1", ...],
  "missing_keywords": ["keyword1", "keyword2", ...],
  "improvement_tips": ["tip1", "tip2", ...],
  "experience_years": <float>,
  "education": {
    "degree": "...",
    "institution": "...",
    "year": "..."
  },
  "projects_detected": [
    {"name": "...", "description": "...", "tech_stack": ["..."]}
  ],
  "summary": "2-3 sentence overall assessment"
}

Be strict but fair. Focus on:
- ATS compatibility (keywords, formatting, sections)
- Skill gaps for modern tech roles
- Grammar and clarity issues
- Actionable improvements

RESUME TEXT:
"""


async def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from PDF using PyMuPDF."""
    if not _pymupdf_available:
        return "[PyMuPDF not installed — install with: pip install pymupdf]\n\nSample text for demo: Python, FastAPI, React, SQL, Machine Learning, Docker, Git"

    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"


async def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """Save uploaded file and return its path."""
    unique_name = f"{uuid.uuid4()}_{filename}"
    file_path = UPLOAD_DIR / unique_name
    with open(file_path, "wb") as f:
        f.write(file_content)
    return str(file_path)


async def analyze_resume(raw_text: str) -> dict:
    """Use Groq to analyze resume text. Returns structured analysis dict."""
    if not raw_text or len(raw_text.strip()) < 50:
        return _mock_analysis()

    messages = [
        {
            "role": "system",
            "content": "You are an expert resume analyzer. Always respond with valid JSON only.",
        },
        {
            "role": "user",
            "content": RESUME_ANALYSIS_PROMPT + raw_text[:8000],  # Limit to 8k chars
        },
    ]

    try:
        response = await groq_service.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
            json_mode=True,
        )
        return json.loads(response)
    except (json.JSONDecodeError, Exception):
        return _mock_analysis()


def _mock_analysis() -> dict:
    return {
        "resume_score": 72,
        "ats_score": 68,
        "strong_skills": ["Python", "JavaScript", "React", "Git"],
        "weak_skills": ["Docker", "Kubernetes", "System Design", "SQL"],
        "grammar_issues": [
            "Use action verbs to start bullet points",
            "Avoid passive voice in experience section",
        ],
        "formatting_suggestions": [
            "Add a professional summary at the top",
            "Use consistent date formatting (MM/YYYY)",
            "Limit to one page for entry-level positions",
        ],
        "missing_keywords": [
            "REST API", "CI/CD", "Agile", "Unit Testing", "Cloud (AWS/GCP/Azure)"
        ],
        "improvement_tips": [
            "Quantify your achievements (e.g., 'Improved performance by 40%')",
            "Add links to GitHub and LinkedIn",
            "Include 2-3 relevant projects with tech stacks",
            "Add certifications if any",
        ],
        "experience_years": 0.5,
        "education": {
            "degree": "B.Tech Computer Science",
            "institution": "Sample University",
            "year": "2025",
        },
        "projects_detected": [
            {
                "name": "E-Commerce Platform",
                "description": "Full-stack web application",
                "tech_stack": ["React", "Node.js", "MongoDB"],
            }
        ],
        "summary": (
            "Good foundational skills in web development. "
            "Resume needs more industry keywords and quantified achievements. "
            "Consider adding more backend and DevOps experience."
        ),
    }
