"""岗位-技能关联实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `job_skill` 表。
描述岗位对技能的要求等级：MUST/NICE/BONUS。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
注意：列名 `required_level`（非 `requirement_level`，区别于 role_skill）。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class JobSkill(Base):
    """岗位-技能关联实体，映射 `job_skill` 表。

    Attributes:
        id: 关联主键，自增 BIGINT。
        job_id: 关联岗位主键。
        skill_id: 关联技能主键。
        importance: 重要性权重（浮点数）。
        required_level: 要求等级（MUST/NICE/BONUS），默认 MUST。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "job_skill"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skill.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    required_level: Mapped[str] = mapped_column(String(10), nullable=False, default="MUST")
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
        return (
            f"<JobSkill id={self.id} job_id={self.job_id} "
            f"skill_id={self.skill_id} level={self.required_level}>"
        )
