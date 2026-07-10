"""技能字典实体 ORM 模块。

映射 KingbaseES `zhihire` 库中已有的 `skill` 表。
技能字典为全局共享数据，承载技能名、领域分类与三态合并状态。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime  # 时间类型

from sqlalchemy import BigInteger, DateTime, String, Text, func  # 列类型
from sqlalchemy.orm import Mapped, mapped_column  # 2.0 声明式注解

from app.models.entities.base import Base  # 声明式基类


class Skill(Base):
    """技能字典实体，映射 `skill` 表（库中表名）。

    三态合并模型：ACTIVE 启用、CANDIDATE 待审、MERGED 已并入目标技能。
    用户/岗位技能关联均通过 `skill_id` 引用本表。

    Attributes:
        id: 技能主键，自增 BIGINT。
        name: 技能名称，唯一可读标识。
        category: 技能领域（后端/前端/测试/运维/数据/通用），可空。
        description: 技能描述，可空。
        status: 技能状态（ACTIVE/CANDIDATE/MERGED），默认 ACTIVE。
        merge_target_id: MERGED 时指向目标技能主键，可空。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记（VARCHAR 1），`'0'` 未删 / `'1'` 已删。
    """

    __tablename__ = "skill"  # 对齐库中已有表名

    # 主键：BIGINT 自增，匹配序列 skill_id_seq
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # 技能名称
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    # 技能领域：后端/前端/测试/运维/数据/通用
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # 技能描述
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 技能状态：ACTIVE/CANDIDATE/MERGED，默认 ACTIVE
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    # MERGED 时指向目标技能主键
    merge_target_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
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
        return f"<Skill id={self.id} name={self.name!r} category={self.category!r} status={self.status!r}>"
