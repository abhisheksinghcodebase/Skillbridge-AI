import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, Text, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(Text)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Analysis results
    resume_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strong_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    weak_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    grammar_issues: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    formatting_suggestions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    missing_keywords: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    improvement_tips: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    education: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    projects_detected: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    full_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
