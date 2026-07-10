"""角色-技能关联实体 ORM 模块。

映射 KingbaseES `zhihire` 库中新增的 `role_skill` 表，
描述职业角色对技能的需求级别：MUST（必备）、NICE（加分）、BONUS（锦上添花）。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class RoleSkill(Base):
    """角色-技能关联实体，映射 `role_skill` 表。

    Attributes:
        id: 关联主键，自增 BIGINT。
        role_id: 关联角色主键。
        skill_id: 关联技能主键。
        requirement_level: 需求级别（MUST/NICE/BONUS），默认 MUST。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "role_skill"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("role.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skill.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    requirement_level: Mapped[str] = mapped_column(
        String(10), nullable=False, default="MUST",
    )
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
            f"<RoleSkill id={self.id} role_id={self.role_id} "
            f"skill_id={self.skill_id} level={self.requirement_level}>"
        )
