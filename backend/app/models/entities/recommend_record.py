"""推荐记录实体 ORM 模块。

映射 KingbaseES `zhihire` 库中 `recommend_record` 表，
记录为用户/企业推荐的岗位/候选人及交互行为。
"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class RecommendRecord(Base):
    """推荐记录实体，映射 `recommend_record` 表。

    Attributes:
        id: 推荐记录主键，自增 BIGINT。
        user_id: 被推荐用户主键，FK -> user.id。
        resume_id: 简历主键（企业端候选人推荐时使用），可空，FK -> resume.id。
        job_id: 推荐的岗位主键，FK -> job.id。
        score: 推荐匹配分。
        recommend_type: 推荐方向（JOB=求职者推荐岗位 / TALENT=企业推荐候选人）。
        is_clicked: 是否已点击查看。
        is_applied: 是否已投递。
        is_invited: 是否已被企业邀请。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "recommend_record"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    resume_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("resume.id", ondelete="SET NULL"), nullable=True,
    )
    job_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommend_type: Mapped[str] = mapped_column(String(10), nullable=False, default="JOB")
    is_clicked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_invited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
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
        return f"<RecommendRecord id={self.id} user_id={self.user_id} job_id={self.job_id} type={self.recommend_type}>"
