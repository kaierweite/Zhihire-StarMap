"""Resume optimization ORM entity."""
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.entities.base import Base

class ResumeOptimization(Base):
    __tablename__ = "resume_optimization"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    job_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    suggestions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[str] = mapped_column(String(1), nullable=False, server_default=func.text("'0'::character varying"))
    def __repr__(self) -> str:
        return f"<ResumeOptimization id={self.id} resume_id={self.resume_id}>"
