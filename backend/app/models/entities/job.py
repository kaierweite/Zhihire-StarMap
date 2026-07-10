"""岗位实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `job` 表。
岗位由企业发布，关联职业角色与技能要求。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class Job(Base):
    """岗位实体，映射 `job` 表（库中已有表名）。

    岗位属于企业（company），可选关联职业角色（occupation_role），
    通过 job_skill 关联技能及其要求等级。
    """

    __tablename__ = "job"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("company.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    occupation_role_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("occupation_role.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    education_requirement: Mapped[str | None] = mapped_column(String(20), nullable=True)
    experience_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    job_type: Mapped[str] = mapped_column(String(20), nullable=False, default="FULL_TIME")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="MANUAL")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    embedding_cache: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_campus: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # 专业（用于按专业筛选）
    major: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # 岗位分类（用于按职类筛选）
    job_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    benefits: Mapped[list | None] = mapped_column(JSONB, nullable=True)
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
        return f"<Job id={self.id} title={self.title!r} company_id={self.company_id}>"
