"""Interview report ORM entity."""
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.entities.base import Base

class InterviewReport(Base):
    __tablename__ = "interview_report"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, unique=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    radar: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feedback: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[str] = mapped_column(String(1), nullable=False, server_default=func.text("'0'::character varying"))
    def __repr__(self) -> str:
        return f"<InterviewReport id={self.id} session_id={self.session_id}>"
