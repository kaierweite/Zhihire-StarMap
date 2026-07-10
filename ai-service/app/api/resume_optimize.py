"""
简历优化路由
"""

from fastapi import APIRouter

from app.models.request import ResumeOptimizeRequest
from app.models.response import ResultWrapper, ResumeOptimizeResponse, ResumeSuggestion
from app.infrastructure.llm_client import llm_client

router = APIRouter(prefix="/ai", tags=["简历优化"])


@router.post("/resume/optimize", response_model=ResultWrapper)
async def resume_optimize(req: ResumeOptimizeRequest):
    """POST /ai/resume/optimize — 简历优化建议"""
    prompt = (
        "你是简历优化专家。请根据以下信息给出简历优化建议。\n\n"
        f"简历 ID: {req.resume_id}\n"
        f"目标岗位 ID: {req.job_id}\n\n"
        "请针对以下板块给出优化建议（JSON 格式）：\n"
        '[{"section": "板块名", "current": "当前内容摘要", "suggestion": "优化建议"}]'
    )
    try:
        result = await llm_client.chat_json(prompt, temperature=0.5)
        if isinstance(result, list):
            items = [ResumeSuggestion(**s) for s in result]
            return ResultWrapper(data=ResumeOptimizeResponse(suggestions=items))
    except Exception:
        pass
    # 降级：返回通用建议
    return ResultWrapper(
        data=ResumeOptimizeResponse(
            suggestions=[
                ResumeSuggestion(section="技能", current="", suggestion="建议补充目标岗位要求的核心技能"),
                ResumeSuggestion(section="经历", current="", suggestion="建议用 STAR 法则描述项目经历"),
                ResumeSuggestion(section="教育", current="", suggestion="建议突出与岗位相关的课程或项目"),
            ]
        )
    )
