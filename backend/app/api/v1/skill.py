"""技能字典 API 路由。

提供技能搜索等基础查询端点。
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.schemas.result import Result
from app.repositories import skill_repository

router = APIRouter(prefix="/skills", tags=["技能"])


@router.get("", summary="搜索技能")
async def search_skills(
    search: str = Query("", max_length=100),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """按名称模糊搜索技能（ILIKE），用于前端技能下拉选择器。"""
    skills = await skill_repository.search_by_name(db, search, limit)
    items = [{"id": s.id, "name": s.name, "category": s.category} for s in skills]
    return Result.success(data=items)
