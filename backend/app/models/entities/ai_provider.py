"""AI Provider ORM entity for admin AI model config.

Stores provider credentials and model configuration.
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class AiProvider(Base):
    """AI 模型提供商配置实体。

    Attributes:
        id: 主键。
        provider_name: 提供商名称（deepseek / openai / tongyi）。
        display_name: 显示名称（DeepSeek / OpenAI / 通义千问）。
        api_key: API Key（存储时做掩码处理）。
        base_url: API 基础地址。
        models: 可用模型列表 JSONB，如 ['deepseek-chat']。
        order_no: 排序序号。
        status: 启用状态（NORMAL / DISABLED）。
        created_at: 创建时间。
        updated_at: 更新时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "ai_provider"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    models: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    order_no: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[str] = mapped_column(
        String(1), nullable=False, server_default=text("'0'")
    )

    def __repr__(self) -> str:
        return f"<AiProvider id={self.id} name={self.provider_name!r}>"

