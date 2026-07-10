"""职业角色实体 ORM 模块。

映射 KingbaseES `zhihire` 库中新增的 `role` 表，
描述职业角色（如"前端开发工程师"）及其所属类别。
软删除标记 `deleted_at` 为 VARCHAR `'0'/'1'`。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class Role(Base):
    """职业角色实体，映射 `role` 表。

    角色分类（category）示例：技术研发 / 产品设计 / 数据算法 / 测试运维 / 市场运营 / 通用。

    Attributes:
        id: 角色主键，自增 BIGINT。
        name: 角色名称（如"前端开发工程师"），唯一。
        description: 角色描述，可空。
        category: 角色所属类别，可空。
        status: 状态 NORMAL/DISABLED，默认 NORMAL。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL")
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
        return f"<Role id={self.id} name={self.name!r} category={self.category!r}>"
