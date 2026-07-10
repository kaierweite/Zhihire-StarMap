"""Interview question ORM entity."""
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.entities.base import Base

class InterviewQuestion(Base):
    __tablename__ = "interview_question"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False, default="TECHNICAL")
    content: Mapped[str] = mapped_column(String(2000), nullable=False)
    expected_points: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    order_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_bank_visible: Mapped[str] = mapped_column(String(1), nullable=False, default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[str] = mapped_column(String(1), nullable=False, server_default=func.text("'0'::character varying"))
    def __repr__(self) -> str:
        return f"<InterviewQuestion id={self.id} session_id={self.session_id}>"
