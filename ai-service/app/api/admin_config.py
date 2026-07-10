"""
Internal admin config API — refresh AI model configs from DB into llm_client runtime.
Called by Spring Boot after admin saves/deletes configs.
"""

import json
import logging

from fastapi import APIRouter

from app.infrastructure.db_client import db_client
from app.infrastructure.llm_client import llm_client, LLMProvider

logger = logging.getLogger("zhihire.ai.config")

router = APIRouter(prefix="/ai/internal", tags=["internal"])


async def _load_configs_into_runtime() -> int:
    """Read ai_model_config from DB and update llm_client providers. Returns count."""
    rows = await db_client.fetch_ai_configs()
    loaded = 0
    for row in rows:
        if not row.get("enabled"):
            continue
        models = []
        raw = row.get("models_json")
        if raw:
            try:
                models = json.loads(raw) if isinstance(raw, str) else raw
            except (json.JSONDecodeError, TypeError):
                models = []
        provider = LLMProvider(
            id=row["provider_id"],
            name=row.get("name", row["provider_id"]),
            base_url=row.get("base_url", ""),
            api_key=row.get("api_key", ""),
            default_model=row.get("default_model", ""),
            temperature=float(row.get("temperature") or 0.7),
            max_tokens=int(row.get("max_tokens") or 4096),
            enabled=True,
        )
        llm_client.update_provider(provider)
        loaded += 1
    logger.info("Loaded %d AI provider configs from DB", loaded)
    return loaded


@router.post("/refresh-config")
async def refresh_config():
    """POST /ai/internal/refresh-config — reload all AI configs from DB."""
    try:
        count = await _load_configs_into_runtime()
        return {"code": 200, "message": "ok", "data": {"loaded": count}}
    except Exception as e:
        logger.error("Failed to refresh AI configs: %s", e)
        return {"code": 500, "message": str(e), "data": None}
