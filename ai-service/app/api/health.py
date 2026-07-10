"""
健康检查路由
"""

from fastapi import APIRouter

from app.models.response import HealthResponse

router = APIRouter(prefix="/ai", tags=["健康检查"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """GET /ai/health — 服务存活探针"""
    return HealthResponse(status="ok")
