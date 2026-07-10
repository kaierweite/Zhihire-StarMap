"""
推荐路由 — 匹配评分
"""

from fastapi import APIRouter

from app.models.request import MatchRequest
from app.models.response import ResultWrapper, MatchResponse, MatchResultItem
from app.services.recommend_service import match_candidates

router = APIRouter(prefix="/ai", tags=["匹配推荐"])


@router.post("/recommend/match", response_model=ResultWrapper)
async def recommend_match(req: MatchRequest):
    """POST /ai/recommend/match — 匹配评分"""
    results = await match_candidates(req.user_skills, req.candidates)
    items = [MatchResultItem(**r) for r in results]
    return ResultWrapper(data=MatchResponse(results=items))
