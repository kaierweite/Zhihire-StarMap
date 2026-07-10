"""?????? ORM ????? KingbaseES zhihire ???? parse_task ??"""
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.entities.base import Base


class ParseTask(Base):
    __tablename__ = "parse_task"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="WAITING")
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[str] = mapped_column(String(1), nullable=False, server_default=func.text("'0'::character varying"))

    def __repr__(self) -> str:
        return f"<ParseTask id={self.id} file_id={self.file_id} status={self.status!r}>"
