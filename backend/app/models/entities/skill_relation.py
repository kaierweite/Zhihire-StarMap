"""技能关系关联实体 ORM 模块。

映射 KingbaseES `zhihire` 库中新增的 `skill_relation` 表，
描述技能之间的四类语义关系（前置依赖/父子包含/相似/互补）。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class SkillRelation(Base):
    """技能关系实体，映射 `skill_relation` 表。

    四类关系边：
    - PREREQUISITE — 前置依赖（学 Vue 前先学 HTML）
    - INCLUDES — 父子包含（前端开发 INCLUDES Vue 3）
    - SIMILAR — 相似技能（Vue 3 ~ React）
    - COMPLEMENTARY — 互补技能（Docker + K8s）
    """

    __tablename__ = "skill_relation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    skill_id_a: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skill.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    skill_id_b: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skill.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    relation_type: Mapped[str] = mapped_column(String(20), nullable=False, default="SIMILAR")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
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
            f"<SkillRelation id={self.id} "
            f"{self.skill_id_a} --[{self.relation_type}]--> {self.skill_id_b}>"
        )
