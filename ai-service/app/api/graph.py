"""
图谱路由 — 构建 / 重载
"""

from fastapi import APIRouter

from app.models.request import GraphBuildRequest
from app.models.response import ResultWrapper, GraphData
from app.services.graph_service import reload_graph, build_graph

router = APIRouter(prefix="/ai", tags=["能力图谱"])


@router.post("/graph/build", response_model=ResultWrapper)
async def graph_build(req: GraphBuildRequest):
    """POST /ai/graph/build — 构建图谱，返回 ECharts JSON"""
    data = await build_graph(req.skills, req.relations)
    return ResultWrapper(data=GraphData(**data))


@router.post("/graph/reload", response_model=ResultWrapper)
async def graph_reload():
    """POST /ai/graph/reload — 从 DB 全量重建内存图"""
    stats = await reload_graph()
    return ResultWrapper(data=stats)
