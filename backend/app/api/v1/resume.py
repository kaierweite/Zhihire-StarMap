"""???????

??????????????????? AI ???????
- POST /api/resume/upload ? ??????
- GET /api/resume ? ????????
- GET /api/resume/{resume_id} ? ????
- PUT /api/resume/{resume_id} ? ??????
- DELETE /api/resume/{resume_id} ? ???
- POST /api/resume/optimize ? AI ??????
"""
from fastapi import APIRouter, BackgroundTasks, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.resume import (
    OptimizeRequest,
    OptimizeResult,
    ResumeContent,
    ResumeDetail,
    ResumeListItem,
    ResumeUploadResult,
)
from app.models.schemas.result import Result, PageResult
from app.services import resume_service
from app.services.errors import BusinessError
from app.services.parse_service import run_parse_pipeline, sync_resume_to_profile

router = APIRouter(prefix="/resume", tags=["??"])


@router.post("/upload", summary="????")
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None),
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[ResumeUploadResult]:
    """???????PDF/DOC/DOCX?????????

    BackgroundTasks ??????????
    """
    try:
        result = await resume_service.upload_resume(db, current_user, file, title)
        # ??????
        background_tasks.add_task(run_parse_pipeline, result.file_id, current_user.id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="?????????")


@router.get("", summary="???????")
async def list_resumes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[PageResult]:
    """?????????????page/size??
    ???? size ??? 50??????? 20??????????????
    """
    try:
        items, total = await resume_service.list_resumes(db, current_user, page, size)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=PageResult(records=[i.model_dump() for i in items], total=total, page=page, size=size))


@router.get("/{resume_id}", summary="????")
async def get_resume(
    resume_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[ResumeDetail]:
    """????????????"""
    try:
        detail = await resume_service.get_resume_detail(db, current_user, resume_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=detail)


@router.put("/{resume_id}", summary="??????")
async def update_resume(
    resume_id: int,
    form: ResumeContent,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[ResumeDetail]:
    """?????????????"""
    try:
        detail = await resume_service.update_resume_content(
            db, current_user, resume_id, title=form.title, content_text=form.content_text)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=detail, message="????")


@router.delete("/{resume_id}", summary="????")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[None]:
    """??????"""
    try:
        await resume_service.delete_resume(db, current_user, resume_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(message="????")


@router.post("/{resume_id}/sync-profile", summary="???????")
async def sync_profile(
    resume_id: int,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[dict]:
    """???????????????????????

    ??????????????? company+title ???
    ??????????????????????
    """
    try:
        result = await sync_resume_to_profile(db, current_user.id, resume_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result, message="????")


@router.post("/optimize", summary="AI ????")
async def optimize_resume(
    form: OptimizeRequest,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result[OptimizeResult]:
    """AI ????????????"""
    try:
        result = await resume_service.optimize_resume(
            db, current_user, form.resume_id, job_description=form.job_description)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result)
