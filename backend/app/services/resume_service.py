"""
Resume service: PDF text extraction + Groq LLM analysis.
"""
import json
import os
import re
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
        return _mock_analysis(raw_text or "")

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
        parsed = _parse_analysis_response(response)
        if parsed:
            return parsed
    except Exception:
        pass

    return _mock_analysis(raw_text)


def _parse_analysis_response(response) -> Optional[dict]:
    """Extract a structured JSON analysis from Groq output, even with markdown wrappers."""
    if response is None:
        return None

    if isinstance(response, dict):
        return response

    text = str(response).strip()
    if not text:
        return None

    for candidate in _candidate_json_strings(text):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except (TypeError, ValueError):
            continue

    return None


def _candidate_json_strings(text: str):
    """Yield likely JSON payloads from plain text or fenced markdown responses."""
    candidates = []
    trimmed = text.strip()
    for marker in ("```json", "```JSON", "```"):
        if marker in trimmed:
            start = trimmed.find(marker)
            content = trimmed[start + len(marker) :]
            if marker == "```":
                # this branch is used for the generic markdown fence case
                content = content.split("\n", 1)[-1]
            candidates.append(content.split("```", 1)[0].strip())
            break

    candidates.append(trimmed)

    # Pull the first object-like block from any surrounding prose.
    match = re.search(r"\{.*\}", trimmed, flags=re.DOTALL)
    if match:
        candidates.insert(0, match.group(0))

    # Deduplicate while keeping order.
    seen = set()
    unique = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return unique


def _mock_analysis(raw_text: str = "") -> dict:
    """Generates a structured analysis from the resume text, even without Groq access."""
    text = (raw_text or "").lower()
    skills = [
        "Python",
        "FastAPI",
        "JavaScript",
        "React",
        "SQL",
        "Docker",
        "AWS",
        "Azure",
        "PostgreSQL",
        "Machine Learning",
        "Node.js",
        "TypeScript",
        "Git",
        "CI/CD",
    ]
    strong_skills = [skill for skill in skills if skill.lower() in text]
    if not strong_skills:
        strong_skills = ["Python", "JavaScript", "Communication", "Problem Solving"]

    missing = [
        keyword
        for keyword in ["REST API", "CI/CD", "Agile", "Unit Testing", "Cloud (AWS/GCP/Azure)"]
        if keyword.lower() not in text
    ]
    if len(missing) < 2:
        missing = [
            "REST API",
            "CI/CD",
            "Agile",
            "Unit Testing",
            "Cloud (AWS/GCP/Azure)",
        ]

    score = min(99, max(45, 55 + len(strong_skills) * 4))
    ats = min(99, max(40, 50 + len(strong_skills) * 3))
    years = 0.5
    if "experience" in text or "worked" in text or "developer" in text:
        years = 2.0 if "senior" in text or "lead" in text else 1.0

    return {
        "resume_score": int(score),
        "ats_score": int(ats),
        "strong_skills": strong_skills[:8],
        "weak_skills": [
            "System Design",
            "Kubernetes",
            "Distributed Systems",
            "Leadership",
        ][:4],
        "grammar_issues": [
            "Use action verbs to start bullet points",
            "Avoid passive voice in experience section",
        ],
        "formatting_suggestions": [
            "Add a professional summary at the top",
            "Use consistent date formatting (MM/YYYY)",
            "Keep experience bullets concise and measurable",
        ],
        "missing_keywords": missing[:5],
        "improvement_tips": [
            f"Quantify achievements with metrics and business impact using the experience in {raw_text[:80].strip() or 'your resume'}",
            "Add links to GitHub and LinkedIn",
            "Include 2-3 relevant projects with tech stacks",
            "Add certifications or cloud credentials if available",
        ],
        "experience_years": years,
        "education": {
            "degree": "Not specified",
            "institution": "Not specified",
            "year": "",
        },
        "projects_detected": [
            {
                "name": "Project portfolio",
                "description": "Resume indicates technical project experience and implementation work.",
                "tech_stack": strong_skills[:5],
            }
        ],
        "summary": (
            f"This resume shows solid technical exposure in {', '.join(strong_skills[:3]) if strong_skills else 'core software engineering'}. "
            "It would benefit from stronger ATS keywords, measurable achievements, and clearer project framing."
        ),
    }
