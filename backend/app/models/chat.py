import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    role: str  # "user" | "assistant"
    content: str
    session_id: Optional[str] = None
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
    def from_doc(cls, doc: Any) -> Optional["ChatMessage"]:
        """Construct ChatMessage instance from MongoDB document dict."""
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


class Roadmap(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    goal: str
    roadmap_data: Dict[str, Any]
    progress: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}

    def to_doc(self) -> dict:
        """Convert model instance to MongoDB document dict."""
        data = self.model_dump()
        data["_id"] = str(self.id)
        data["id"] = str(self.id)
        data["user_id"] = str(self.user_id)
        return data

    @classmethod
    def from_doc(cls, doc: Any) -> Optional["Roadmap"]:
        """Construct Roadmap instance from MongoDB document dict."""
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


class GitHubAnalysis(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    github_username: str
    analysis_data: Dict[str, Any]
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
    def from_doc(cls, doc: Any) -> Optional["GitHubAnalysis"]:
        """Construct GitHubAnalysis instance from MongoDB document dict."""
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


class LearningProgress(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    skill_name: str
    category: Optional[str] = None
    progress_percent: int = 0
    status: str = "not_started"
    notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}

    def to_doc(self) -> dict:
        """Convert model instance to MongoDB document dict."""
        data = self.model_dump()
        data["_id"] = str(self.id)
        data["id"] = str(self.id)
        data["user_id"] = str(self.user_id)
        return data

    @classmethod
    def from_doc(cls, doc: Any) -> Optional["LearningProgress"]:
        """Construct LearningProgress instance from MongoDB document dict."""
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


class InterviewSession(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    topic: str
    question: str
    answer: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None
    score: Optional[int] = None
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
    def from_doc(cls, doc: Any) -> Optional["InterviewSession"]:
        """Construct InterviewSession instance from MongoDB document dict."""
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
