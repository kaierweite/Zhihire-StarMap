"""
职业规划路由
"""

from fastapi import APIRouter

from app.models.request import CareerAnalyzeRequest
from app.models.response import ResultWrapper, CareerAnalyzeResponse, CareerPlanItem
from app.services.career_service import analyze_career

router = APIRouter(prefix="/ai", tags=["职业规划"])


@router.post("/career/analyze", response_model=ResultWrapper)
async def career_analyze(req: CareerAnalyzeRequest):
    """POST /ai/career/analyze — 职业规划分析"""
    result = await analyze_career(req.user_skills, req.target_role)
    items = [CareerPlanItem(**p) for p in result["learning_path"]]
    data = CareerAnalyzeResponse(
        gap_skills=result["gap_skills"],
        learning_path=items,
        rationale=result["rationale"],
    )
    return ResultWrapper(data=data)
