"""AI 模型配置业务服务。"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.ai_provider import AiProvider
from app.models.schemas.admin import (
    AiProviderCreateRequest,
    AiProviderItem,
    AiProviderTestResult,
    AiProviderUpdateRequest,
)
from app.repositories import ai_provider_repository as repo
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)

def _mask_api_key(key):
    if not key or len(key) < 8: return key
    return key[:4] + chr(42) * (len(key) - 8) + key[-4:]

async def list_providers(db):
    providers = await repo.list_all(db)
    return [_to_item(p) for p in providers]

async def create_provider(db, req):
    existing = await repo.get_by_name(db, req.provider_name)
    if existing:
        raise BusinessError(400, "Provider " + req.provider_name + " exists")
    p = AiProvider(provider_name=req.provider_name, display_name=req.display_name,
                   api_key=req.api_key, base_url=req.base_url,
                   models=req.models, order_no=req.order_no)
    created = await repo.create(db, p)
    await db.commit()
    await db.refresh(created)
    return _to_item(created)

async def update_provider(db, provider_id, req):
    provider = await repo.get_by_id(db, provider_id)
    if provider is None:
        raise BusinessError(404, "AI provider not found")
    values = req.model_dump(exclude_none=True)
    if values:
        updated = await repo.update(db, provider, values)
        await db.commit()
        await db.refresh(updated)
    else:
        updated = provider
    return _to_item(updated)

async def test_connection(db, provider_id):
    provider = await repo.get_by_id(db, provider_id)
    if provider is None:
        raise BusinessError(404, "AI provider not found")
    if not provider.api_key:
        return AiProviderTestResult(success=False, latency_ms=None, message="API Key not configured")
    return AiProviderTestResult(success=True, latency_ms=0, message="Connection test passed (mock)")

async def delete_provider(db, provider_id):
    provider = await repo.get_by_id(db, provider_id)
    if provider is None:
        raise BusinessError(404, "AI provider not found")
    await repo.delete(db, provider)
    await db.commit()

def _to_item(p):
    return AiProviderItem(
        id=p.id, provider_name=p.provider_name,
        display_name=p.display_name,
        api_key=_mask_api_key(p.api_key),
        base_url=p.base_url, models=p.models,
        order_no=p.order_no, status=p.status,
        created_at=p.created_at, updated_at=p.updated_at)