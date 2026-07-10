"""技能同义词实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `skill_synonym` 表，
支撑技能归一时将用户输入的各种写法映射到标准 skill_id。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime  # 时间类型

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func  # 列类型
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类


class SkillSynonym(Base):
    """技能同义词实体，映射 `skill_synonym` 表（库中表名）。

    每条记录将一个同义写法（synonym）关联到标准技能 skill_id，
    用于技能归一时消除大小写/分隔符/缩写等写法差异。

    Attributes:
        id: 主键，自增 BIGINT。
        skill_id: 关联技能主键。
        synonym: 同义写法（如 "SpringBoot"）。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记（VARCHAR 1），`'0'` 未删 / `'1'` 已删。
    """

    __tablename__ = "skill_synonym"  # 对齐库中已有表名

    # 主键：BIGINT 自增
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 关联技能主键
    skill_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("skill.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 同义写法：如 SpringBoot/Spring-Boot/vue3 等
    synonym: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
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
        return f"<SkillSynonym id={self.id} skill_id={self.skill_id} synonym={self.synonym!r}>"
