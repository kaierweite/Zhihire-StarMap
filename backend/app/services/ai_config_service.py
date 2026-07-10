"AI 模型配置业务服务。"
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


def _mask_api_key(key: str | None) -> str | None:
    if not key or len(key) < 8:
        return key
    return key[:4] + * * (len(key) - 8) + key[-4:]


async def list_providers(db: AsyncSession) -> list[AiProviderItem]:
    providers = await repo.list_all(db)
    return [
        AiProviderItem(
            id=p.id,
            provider_name=p.provider_name,
            display_name=p.display_name,
            api_key=_mask_api_key(p.api_key),
            base_url=p.base_url,
            models=p.models,
            order_no=p.order_no,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in providers
    ]


async def create_provider(db: AsyncSession, req: AiProviderCreateRequest) -> AiProviderItem:
    existing = await repo.get_by_name(db, req.provider_name)
    if existing:
        raise BusinessError(400, 提供商  + req.provider_name +  已存在)
    provider = AiProvider(
        provider_name=req.provider_name,
        display_name=req.display_name,
        api_key=req.api_key,
        base_url=req.base_url,
        models=req.models,
        order_no=req.order_no,
    )
    created = await repo.create(db, provider)
    await db.commit()
    return _to_item(created)


async def update_provider(db: AsyncSession, provider_id: int, req: AiProviderUpdateRequest) -> AiProviderItem:
    provider = await repo.get_by_id(db, provider_id)
    if provider is None:
        raise BusinessError(404, AI 提供商不存在)
    values = req.model_dump(exclude_none=True)
    if values:
        updated = await repo.update(db, provider, values)
        await db.commit()
    else:
        updated = provider
    return _to_item(updated)


async def test_connection(db: AsyncSession, provider_id: int) -> AiProviderTestResult:
    provider = await repo.get_by_id(db, provider_id)
    if provider is None:
        raise BusinessError(404, AI 提供商不存在)
    if not provider.api_key:
        return AiProviderTestResult(success=False, latency_ms=None, message=API Key 未配置)
    return AiProviderTestResult(success=True, latency_ms=0, message=连接测试完成（mock）)


async def delete_provider(db: AsyncSession, provider_id: int) -> None:
    provider = await repo.get_by_id(db, provider_id)
    if provider is None:
        raise BusinessError(404, AI 提供商不存在)
    await repo.delete(db, provider)
    await db.commit()


def _to_item(p: AiProvider) -> AiProviderItem:
    return AiProviderItem(
        id=p.id,
        provider_name=p.provider_name,
        display_name=p.display_name,
        api_key=_mask_api_key(p.api_key),
        base_url=p.base_url,
        models=p.models,
        order_no=p.order_no,
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )
