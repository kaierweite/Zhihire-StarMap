"""
数据库客户端 — 只读查询 skill / relation 数据用于图谱重建
"""

import asyncpg

from app.infrastructure.config_manager import settings


class DBClient:
    """KingbaseES（PostgreSQL 兼容）只读客户端"""

    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def init(self) -> None:
        """初始化连接池"""
        self._pool = await asyncpg.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            min_size=1,
            max_size=5,
        )

    async def close(self) -> None:
        """关闭连接池"""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def fetch_skills(self) -> list[dict]:
        """查询所有技能节点"""
        if not self._pool:
            return []
        rows = await self._pool.fetch(
            "SELECT id, name, category FROM skill WHERE deleted_at IS NULL"
        )
        return [dict(row) for row in rows]

    async def fetch_relations(self) -> list[dict]:
        """查询所有技能关系"""
        if not self._pool:
            return []
        rows = await self._pool.fetch(
            "SELECT source_id, target_id, relation_type, weight FROM skill_relation WHERE deleted_at IS NULL"
        )
        return [dict(row) for row in rows]


# 全局单例
db_client = DBClient()
