"""
文档解析路由 — 简历解析 + 岗位 JD 解析
"""

from fastapi import APIRouter

from app.models.request import ResumeParseRequest, JobParseRequest
from app.models.response import ResultWrapper, ParseResult
from app.services.parse_service import parse_resume, parse_job

router = APIRouter(prefix="/ai", tags=["文档解析"])


@router.post("/parse/resume", response_model=ResultWrapper)
async def resume_parse(req: ResumeParseRequest):
    """POST /ai/parse/resume — 简历解析"""
    result = await parse_resume(req.file_path)
    return ResultWrapper(data=ParseResult(**result))


@router.post("/parse/job", response_model=ResultWrapper)
async def job_parse(req: JobParseRequest):
    """POST /ai/parse/job — 岗位 JD 解析"""
    result = await parse_job(req.file_path)
    return ResultWrapper(data=ParseResult(**result))
