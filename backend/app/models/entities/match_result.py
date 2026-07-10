"""匹配结果实体 ORM 模块。

映射 KingbaseES `zhihire` 库中 `match_result` 表，
记录简历与岗位的匹配评分结果（懒计算 + 新鲜度缓存）。
"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class MatchResult(Base):
    """匹配结果实体，映射 `match_result` 表。

    Attributes:
        id: 匹配结果主键，自增 BIGINT。
        resume_id: 简历主键，FK -> resume.id。
        job_id: 岗位主键，FK -> job.id。
        score: 匹配总分（0~100）。
        match_detail: 匹配明细 JSONB（含 breakdown 四维度子分 + rationale）。
        is_stale: 是否过期（简历/岗位技能变更后标记，触发重算）。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "match_result"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("resume.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    job_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    match_detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_stale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
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
        return f"<MatchResult id={self.id} resume_id={self.resume_id} job_id={self.job_id} score={self.score}>"
