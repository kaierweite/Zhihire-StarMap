"""职业规划 API 路由（Day07）。

3 个端点：
- POST /api/career/plan/generate — 基于图谱算法生成职业规划
- GET  /api/career/plan — 获取已生成的规划
- POST /api/career/plan/ai-generate — AI 驱动生成（专业/JD 输入 + 思维导图）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.entities.user import User
from app.models.enums.role import RoleEnum
from app.models.schemas.career import CareerPlanGenerateRequest, AiPlanGenerateRequest
from app.models.schemas.result import Result
from app.services import career_service
from app.services.errors import BusinessError

router = APIRouter(prefix="/career", tags=["职业规划"])


@router.post("/plan/generate", summary="生成职业规划")
async def generate_plan(
    req: CareerPlanGenerateRequest,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """用户选择目标职业角色，基于图谱算法生成有序学习路径规划。"""
    try:
        result = await career_service.generate_plan(db, current_user.id, req.target_role_id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result.model_dump())


@router.get("/plan", summary="获取职业规划")
async def get_plan(
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """获取当前用户最新生成的职业规划。"""
    try:
        plan = await career_service.get_plan(db, current_user.id)
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)

    if plan is None:
        return Result.success(data=None, message="尚未生成职业规划")

    # plan_content 是 JSONB，已直接解析为 dict
    plan_data = plan.plan_content or {}
    plan_data["id"] = plan.id
    plan_data["target_role"] = plan.target_role
    plan_data["target_role_id"] = plan.target_role_id
    plan_data["source"] = plan.source
    plan_data["created_at"] = str(plan.created_at) if plan.created_at else None
    plan_data["updated_at"] = str(plan.updated_at) if plan.updated_at else None

    return Result.success(data=plan_data)


@router.post("/plan/ai-generate", summary="AI 生成职业规划")
async def ai_generate_plan(
    req: AiPlanGenerateRequest,
    current_user: User = Depends(require_role(RoleEnum.USER)),
    db: AsyncSession = Depends(get_db),
) -> Result:
    """用户输入专业名称或粘贴岗位 JD，AI 分析差距并生成学习路径思维导图。"""
    try:
        result = await career_service.ai_generate_plan(
            db,
            current_user.id,
            input_type=req.input_type,
            target_text=req.target_text,
        )
    except BusinessError as exc:
        return Result.error(code=exc.code, message=exc.message, data=exc.data)
    return Result.success(data=result)
