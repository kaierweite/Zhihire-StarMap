"""职业规划实体 ORM 模块。

映射 KingbaseES `zhihire` 库中新增的 `career_plan` 表，
存储用户对目标职业角色的规划分析结果（缺口技能 + 学习路径 + 图提示）。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class CareerPlan(Base):
    """职业规划实体，映射 `career_plan` 表。

    Attributes:
        id: 规划主键，自增 BIGINT。
        user_id: 用户主键（关联 user 表）。
        target_role: 目标职业角色名。
        target_role_id: 目标角色主键（关联 role 表）。
        plan_content: 规划结果 JSONB（含 gap_skills / learning_path / graph_hints / rationale 等字段）。
        source: 规划来源（INTERVIEW / PROACTIVE / RECOMMEND），默认 PROACTIVE。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "career_plan"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True,
    )
    target_role: Mapped[str] = mapped_column(String(100), nullable=False)
    target_role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    plan_content: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="PROACTIVE")
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
            f"<CareerPlan id={self.id} user_id={self.user_id} "
            f"target_role={self.target_role!r} source={self.source!r}>"
        )
