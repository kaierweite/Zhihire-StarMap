"""Notification ORM entity."""
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.entities.base import Base


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False, default="SYSTEM")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    deleted_at: Mapped[str] = mapped_column(
        String(1), nullable=False, server_default=text("'0'")
    )

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} user_id={self.user_id}"
            f" type={self.type!r} is_read={self.is_read}>"
        )
