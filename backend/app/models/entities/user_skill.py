"""用户技能关联实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `user_skill` 表，
描述用户与技能的多对多关联及熟练度。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime  # 时间类型

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, func  # 列类型
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类


class UserSkill(Base):
    """用户技能关联实体，映射 `user_skill` 表（库中表名）。

    一名用户可关联多个技能，通过 `skill_id` 关联到 `skill` 字典表，
    `proficiency_level` 记录熟练度（0~5）。

    Attributes:
        id: 关联主键，自增 BIGINT。
        user_id: 关联用户主键。
        skill_id: 关联技能主键。
        proficiency_level: 熟练度 0~5，默认 0。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记（VARCHAR 1），`'0'` 未删 / `'1'` 已删。
    """

    __tablename__ = "user_skill"  # 对齐库中已有表名

    # 主键：BIGINT 自增，匹配序列 user_skill_id_seq
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 关联用户主键
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 关联技能主键
    skill_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("skill.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 熟练度 0~5，默认 0
    proficiency_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    # 更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # 软删除标记：VARCHAR(1)，'0' 未删 / '1' 已删
    deleted_at: Mapped[str] = mapped_column(String(1), nullable=False, server_default=func.text("'0'::character varying"))

    def __repr__(self) -> str:
        """可读的调试表示。"""
        return f"<UserSkill id={self.id} user_id={self.user_id} skill_id={self.skill_id} level={self.proficiency_level}>"
