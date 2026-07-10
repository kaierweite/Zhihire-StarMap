"""职业角色实体 ORM 模块（独立于 role 表）。

映射 KingbaseES `zhihire` 库中已有的 `occupation_role` 表，
用于岗位选择职业角色（Day05）。
与 Day04 的 role 表结构相同，但表名不同，数据独立。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class OccupationRole(Base):
    """职业角色实体，映射 `occupation_role` 表。

    Attributes:
        id: 角色主键，自增 BIGINT。
        name: 角色名称，唯一。
        description: 角色描述，可空。
        category: 角色所属类别，可空。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "occupation_role"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
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
        return f"<OccupationRole id={self.id} name={self.name!r}>"
