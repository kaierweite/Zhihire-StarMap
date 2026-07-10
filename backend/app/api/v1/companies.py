"""企业相关路由模块。

提供企业名称搜索、企业信息查询等端点。
"""
from fastapi import APIRouter, Depends, Query  # 路由分组与依赖
from sqlalchemy.ext.asyncio import AsyncSession  # 异步会话类型

from app.db.session import get_db  # 数据库会话依赖
from app.models.schemas.result import Result  # 统一响应模型
from app.repositories import company_repository  # 企业仓储


# 路由实例
router = APIRouter(prefix="/companies", tags=["企业"])


@router.get("/search", summary="搜索企业名称")
async def search_companies(
    keyword: str = Query(..., min_length=1, max_length=50, description="搜索关键字"),
    limit: int = Query(10, ge=1, le=50, description="返回条数上限"),
    db: AsyncSession = Depends(get_db),
) -> Result[list[str]]:
    """按关键字模糊搜索现有企业名称，返回匹配的企业名称列表。

    用于注册页面的企业名称自动补全。未登录用户可调用。

    Args:
        keyword: 搜索关键字。
        limit: 返回条数上限，默认 10。
        db: 异步数据库会话。

    Returns:
        Result[list[str]]: 匹配的企业名称列表。
    """
    # 从仓储层查询匹配的企业名称
    names = await company_repository.search_names(db, keyword, limit)
    return Result.success(data=names)
