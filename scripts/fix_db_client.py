# -*- coding: utf-8 -*-
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai-service', 'app', 'infrastructure', 'db_client.py')

content = r'''"""
DB client — read skill/relation/config data for graph rebuild and AI config.
"""

import asyncpg

from app.infrastructure.config_manager import settings


class DBClient:
    """KingbaseES (PostgreSQL compatible) read client."""

    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def init(self) -> None:
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
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def fetch_skills(self) -> list[dict]:
        if not self._pool:
            return []
        rows = await self._pool.fetch(
            "SELECT id, name, category FROM skill WHERE deleted_at = '0'"
        )
        return [dict(row) for row in rows]

    async def fetch_relations(self) -> list[dict]:
        if not self._pool:
            return []
        rows = await self._pool.fetch(
            "SELECT source_id, target_id, relation_type, weight "
            "FROM skill_relation WHERE deleted_at = '0'"
        )
        return [dict(row) for row in rows]

    async def fetch_ai_configs(self) -> list[dict]:
        """Fetch all AI model configs from DB."""
        if not self._pool:
            return []
        rows = await self._pool.fetch(
            "SELECT provider_id, name, enabled, api_key, base_url, "
            "default_model, models_json, temperature, max_tokens, test_status "
            "FROM ai_model_config WHERE deleted_at = '0' ORDER BY id"
        )
        return [dict(row) for row in rows]


# global singleton
db_client = DBClient()
'''

with open(path, 'w', encoding='utf-8') as f:
    f.write(content.lstrip('\n'))

print(f"Written {os.path.getsize(path)} bytes")
