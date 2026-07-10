"""OperationLog ORM entity.

Maps to KingbaseES `operation_log` table (01_schema.sql).
Used by @operation_log decorator for audit trail.
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class OperationLog(Base):
    """操作日志实体，映射 `operation_log` 表。

    Attributes:
        id: 主键，自增 BIGINT。
        user_id: 操作用户主键。
        module: 模块名（如 "用户管理" / "岗位管理" / "字典审核"）。
        action: 操作动作（如 "封禁用户" / "审核通过" / "强制下架"）。
        detail: JSONB 扩展信息（如 target_type / target_id / reason 等）。
        ip: 客户端 IP 地址。
        created_at: 创建时间。
        deleted_at: 软删除标记（VARCHAR 1），'0' 未删 / '1' 已删。
    """

    __tablename__ = "operation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detail: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    deleted_at: Mapped[str] = mapped_column(
        String(1), nullable=False, server_default=text("'0'")
    )

    def __repr__(self) -> str:
        return (
            f"<OperationLog id={self.id} user_id={self.user_id}"
            f" module={self.module!r} action={self.action!r}>"
        )

