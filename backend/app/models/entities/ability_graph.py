"""能力图谱缓存实体 ORM 模块。

映射 KingbaseES `zhihire` 库中新增的 `ability_graph` 表，
以 owner_type + owner_id 标识图谱所属主体（用户/岗位），
`graph_json` 存储 ECharts 关系图 JSON 负载。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.entities.base import Base


class AbilityGraph(Base):
    """能力图谱缓存实体，映射 `ability_graph` 表。

    图谱实际由常驻内存 networkx 对象构建，
    本表仅缓存 ECharts 渲染所需的 JSON payload。

    Attributes:
        id: 缓存主键，自增 BIGINT。
        owner_type: 所属主体类型（USER/JOB）。
        owner_id: 所属主体主键。
        graph_json: ECharts 关系图 JSON 字符串。
        updated_at: 最后更新时间。
        created_at: 创建时间。
        deleted_at: 软删除标记。
    """

    __tablename__ = "ability_graph"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    graph_json: Mapped[str | None] = mapped_column(Text, nullable=True)
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
            f"<AbilityGraph id={self.id} "
            f"owner={self.owner_type}:{self.owner_id}>"
        )
