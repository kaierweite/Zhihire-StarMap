"""简历投递实体 ORM 模块。

映射 KingbaseES `zhihire` 库中新增的 `job_application` 表，
记录用户对岗位的投递行为。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class JobApplication(Base):
    """简历投递实体，映射 `job_application` 表。

    Attributes:
        id: 投递主键，自增 BIGINT。
        user_id: 投递用户主键，FK -> user.id。
        job_id: 目标岗位主键，FK -> job.id。
        resume_id: 使用的简历主键，可空，FK -> resume.id。
        status: 投递状态（APPLIED/REVIEWING/ACCEPTED/REJECTED），默认 APPLIED。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "job_application"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    job_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    resume_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("resume.id", ondelete="SET NULL"), nullable=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="APPLIED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now(),
    )
    deleted_at: Mapped[str] = mapped_column(
        String(1), nullable=False, server_default=func.text("'0'::character varying"),
    )

    def __repr__(self) -> str:
        return f"<JobApplication id={self.id} user_id={self.user_id} job_id={self.job_id} status={self.status!r}>"
