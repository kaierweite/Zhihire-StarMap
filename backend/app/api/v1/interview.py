"Interview API routes (Day08)."
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.interview import InterviewMessageRequest, InterviewStartRequest, InterviewFinishRequest
from app.models.schemas.result import PageResult, Result
from app.services import interview_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/interview", tags=["AI\u9762\u8bd5"])

@router.post("/start", summary="\u5f00\u59cbAI\u6a21\u62df\u9762\u8bd5")
async def start_interview(req: InterviewStartRequest, current_user: User = Depends(require_role(RoleEnum.USER)), db: AsyncSession = Depends(get_db)):
    try:
        r = await interview_service.start_interview(db, current_user.id, req.occupation_role_id, job_id=req.job_id)
    except BusinessError as e: return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(data=r.model_dump())

@router.post("/message", summary="\u63d0\u4ea4\u9762\u8bd5\u56de\u7b54")
async def submit_answer(req: InterviewMessageRequest, current_user: User = Depends(require_role(RoleEnum.USER)), db: AsyncSession = Depends(get_db)):
    try:
        r = await interview_service.submit_answer(db, current_user.id, req.session_id, req.question_id, req.answer)
    except BusinessError as e: return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(data=r.model_dump())

@router.post("/finish", summary="\u624b\u52a8\u7ed3\u675f\u9762\u8bd5\u5e76\u751f\u6210\u62a5\u544a")
async def finish_interview(req: InterviewFinishRequest, current_user: User = Depends(require_role(RoleEnum.USER)), db: AsyncSession = Depends(get_db)):
    try:
        r = await interview_service.finish_interview(db, current_user.id, req.session_id)
    except BusinessError as e: return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(data=r.model_dump())

@router.get("/report/{session_id}", summary="\u83b7\u53d6\u9762\u8bd5\u62a5\u544a")
async def get_report(session_id: int, current_user: User = Depends(require_role(RoleEnum.USER)), db: AsyncSession = Depends(get_db)):
    try:
        r = await interview_service.get_report(db, current_user.id, session_id)
    except BusinessError as e: return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(data=r.model_dump())

@router.get("/question-bank", summary="\u67e5\u8be2\u9762\u8bd5\u9898\u5e93")
async def query_bank(question_type: str | None = Query(None), page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=50), current_user: User = Depends(require_role(RoleEnum.USER)), db: AsyncSession = Depends(get_db)):
    try:
        items, total = await interview_service.query_question_bank(db, question_type=question_type, page=page, size=size)
    except BusinessError as e: return Result.error(code=e.code, message=e.message, data=e.data)
    return Result.success(data=PageResult(records=[i.model_dump() for i in items], total=total, page=page, size=size))
