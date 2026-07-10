"""健康检查路由模块。

提供 `/ping` 端点，供前端与运维探测后端是否存活。
该端点不依赖数据库与外部服务，确保骨架可独立启动。
"""
from fastapi import APIRouter  # 路由分组

from app.models.schemas.result import Result  # 统一响应模型


# 路由实例，供 v1 聚合器挂载
router = APIRouter(prefix="/ping", tags=["健康检查"])


@router.get("", summary="健康检查")
async def ping() -> Result[str]:
    """健康检查端点。

    Returns:
        Result[str]: code=200，data 为 "pong"。
    """
    # 返回统一封装的成功响应，data="pong"
    return Result.success(data="pong", message="success")