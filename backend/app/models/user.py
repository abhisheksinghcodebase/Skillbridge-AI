import uuid
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    email: str
    hashed_password: str
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    skills: Optional[List[str]] = Field(default_factory=list)
    resume_url: Optional[str] = None
    github_username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}

    def to_doc(self) -> dict:
        """Convert model instance to MongoDB document dict."""
        data = self.model_dump()
        data["_id"] = str(self.id)
        data["id"] = str(self.id)
        return data

    @classmethod
    def from_doc(cls, doc: Any) -> Optional["User"]:
        """Construct User instance from MongoDB document dict."""
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
        return cls(**doc_copy)
