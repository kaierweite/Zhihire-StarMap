"""
面试路由 — 出题 / 评答 / 报告
"""

from fastapi import APIRouter

from app.models.request import InterviewQuestionsRequest, InterviewEvaluateRequest, InterviewReportRequest
from app.models.response import ResultWrapper, InterviewQuestionsResponse, InterviewQuestionItem, InterviewEvaluateResponse, InterviewReportResponse
from app.services.interview_service import get_questions, submit_answer, get_report

router = APIRouter(prefix="/ai", tags=["模拟面试"])


@router.post("/interview/questions", response_model=ResultWrapper)
async def interview_questions(req: InterviewQuestionsRequest):
    """POST /ai/interview/questions — 面试出题"""
    questions = await get_questions([], [], req.count)
    items = [InterviewQuestionItem(**q) for q in questions]
    return ResultWrapper(data=InterviewQuestionsResponse(questions=items))


@router.post("/interview/evaluate", response_model=ResultWrapper)
async def interview_evaluate(req: InterviewEvaluateRequest):
    """POST /ai/interview/evaluate — 面试评答"""
    result = await submit_answer("default", req.question_id, "", [], req.answer)
    return ResultWrapper(data=InterviewEvaluateResponse(**result))


@router.post("/interview/report", response_model=ResultWrapper)
async def interview_report(req: InterviewReportRequest):
    """POST /ai/interview/report — 面试报告"""
    result = await get_report(req.session_id)
    return ResultWrapper(data=InterviewReportResponse(**result))
