import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Resume(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    filename: str
    file_path: str
    raw_text: Optional[str] = None

    # Analysis results
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

    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}

    def to_doc(self) -> dict:
        """Convert model instance to MongoDB document dict."""
        data = self.model_dump()
        data["_id"] = str(self.id)
        data["id"] = str(self.id)
        data["user_id"] = str(self.user_id)
        return data

    @classmethod
    def from_doc(cls, doc: Any) -> Optional["Resume"]:
        """Construct Resume instance from MongoDB document dict."""
        if not doc:
            return None
        doc_copy = dict(doc)
        if "id" not in doc_copy and "_id" in doc_copy:
            doc_copy["id"] = doc_copy["_id"]
        if isinstance(doc_copy.get("id"), str):
            try:
                doc_copy["id"] = uuid.UUID(doc_copy["id"])
            except ValueError:
                pass
        if isinstance(doc_copy.get("user_id"), str):
            try:
                doc_copy["user_id"] = uuid.UUID(doc_copy["user_id"])
            except ValueError:
                pass
        return cls(**doc_copy)
