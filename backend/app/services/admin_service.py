"""管理员业务服务模块。

提供后台管理相关的业务编排，包括：
- 实时聚合统计
- 用户管理（列表/封禁/解封）
- 企业审核（列表/通过/驳回）
- 操作日志分页
- 岗位强制下架/恢复
"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.company import Company
from app.models.entities.job import Job
from app.models.entities.job_application import JobApplication
from app.models.entities.match_result import MatchResult
from app.models.entities.parse_task import ParseTask
from app.models.entities.user import User
from app.models.schemas.admin import (
    AdminStatResponse,
    CompanyAuditItem,
    JobAdminItem,
    LogItem,
    SkillAuditItem,
    UserAdminItem,
)
from app.models.schemas.result import PageResult
from app.repositories import company_repository, job_repository, operation_log_repository, skill_repository, user_repository
from app.services.errors import BusinessError


async def get_stat(db: AsyncSession) -> AdminStatResponse:
    """获取后台首页实时聚合统计。

    使用 SQL COUNT 实时聚合用户/企业/岗位/匹配/解析/投递数量。

    Args:
        db: 异步数据库会话。

    Returns:
        AdminStatResponse: 统计结果。
    """
    # 注册用户总数
    user_count = await _count(db, User, User.deleted_at == "0")
    # 注册企业总数
    company_count = await _count(db, Company, Company.deleted_at == "0")
    # 在招岗位总数
    job_count = await _count(db, Job, Job.deleted_at == "0", Job.status == "OPEN")
    # 匹配记录总数
    match_count = await _count(db, MatchResult, MatchResult.deleted_at == "0")
    # 解析任务总数
    parse_count = await _count(db, ParseTask, ParseTask.deleted_at == "0")
    # 简历投递总数
    application_count = await _count(db, JobApplication, JobApplication.deleted_at == "0")

    return AdminStatResponse(
        user_count=user_count,
        company_count=company_count,
        job_count=job_count,
        match_count=match_count,
        parse_count=parse_count,
        application_count=application_count,
    )


async def _count(db: AsyncSession, model, *conditions) -> int:
    """通用的 COUNT 查询辅助方法。"""
    stmt = select(func.count()).select_from(model).where(*conditions)
    result = await db.execute(stmt)
    return result.scalar_one()


async def list_users(
    db: AsyncSession,
    keyword: str | None = None,
    role: str | None = None,
    page: int = 1,
    size: int = 20,
) -> PageResult:
    """获取用户管理分页列表。

    支持按用户名/邮箱/手机号关键词搜索，以及按角色筛选。

    Args:
        db: 异步数据库会话。
        keyword: 搜索关键词（匹配 username / email / phone）。
        role: 按角色筛选（如 USER / COMPANY / ADMIN）。
        page: 页码。
        size: 每页条数。

    Returns:
        PageResult: 分页结果，records 为 UserAdminItem 列表。
    """
    base_cond = [User.deleted_at == "0"]

    if keyword:
        keyword_filter = (
            User.username.ilike(f"%{keyword}%")
            | User.email.ilike(f"%{keyword}%")
            | User.phone.ilike(f"%{keyword}%")
        )
        base_cond.append(keyword_filter)

    if role:
        base_cond.append(User.role == role)

    # 计数
    count_stmt = select(func.count()).select_from(User).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # 分页查询
    query_stmt = (
        select(User)
        .where(*base_cond)
        .order_by(User.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query_stmt)
    users = list(result.scalars().all())

    # 转换为响应模型
    records = [
        UserAdminItem(
            id=u.id,
            username=u.username,
            email=u.email,
            phone=u.phone,
            role=u.role,
            status=u.status,
            avatar_url=u.avatar_url,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]

    return PageResult(records=[r.model_dump(mode="json") for r in records], total=total, page=page, size=size)


async def set_user_status(db: AsyncSession, user_id: int, status: str) -> UserAdminItem:
    """设置用户状态（封禁/解封）。

    Args:
        db: 异步数据库会话。
        user_id: 目标用户主键。
        status: 目标状态，BANNED 或 NORMAL。

    Returns:
        UserAdminItem: 更新后的用户信息。

    Raises:
        BusinessError: 用户不存在或状态非法。
    """
    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise BusinessError(code=404, message="用户不存在")

    if status not in ("BANNED", "NORMAL"):
        raise BusinessError(code=400, message="无效的状态值，仅支持 BANNED / NORMAL")

    user.status = status
    user.updated_at = datetime.now()
    await db.flush()

    return UserAdminItem(
        id=user.id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        role=user.role,
        status=user.status,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


async def list_companies_pending(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
) -> PageResult:
    """获取待审核企业列表。

    Args:
        db: 异步数据库会话。
        page: 页码。
        size: 每页条数。

    Returns:
        PageResult: 分页结果，records 为 CompanyAuditItem 列表。
    """
    base_cond = [
        Company.deleted_at == "0",
        Company.audit_status == "PENDING",
    ]

    count_stmt = select(func.count()).select_from(Company).where(*base_cond)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    query_stmt = (
        select(Company)
        .where(*base_cond)
        .order_by(Company.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query_stmt)
    companies = list(result.scalars().all())

    records = [
        CompanyAuditItem(
            id=c.id,
            company_name=c.company_name,
            industry=c.industry,
            scale=c.scale,
            website=c.website,
            description=c.description,
            address=c.address,
            contact_name=c.contact_name,
            contact_phone=c.contact_phone,
            contact_email=c.contact_email,
            audit_status=c.audit_status,
            audit_reason=c.audit_reason,
            created_at=c.created_at,
        )
        for c in companies
    ]

    return PageResult(records=[r.model_dump(mode="json") for r in records], total=total, page=page, size=size)


async def audit_company(
    db: AsyncSession,
    company_id: int,
    action: str,
    reason: str | None = None,
) -> CompanyAuditItem:
    """审核企业（通过/驳回）。

    Args:
        db: 异步数据库会话。
        company_id: 企业主键。
        action: 审核动作，pass=通过 / reject=驳回。
        reason: 驳回原因（action=reject 时必填）。

    Returns:
        CompanyAuditItem: 更新后的企业信息。

    Raises:
        BusinessError: 企业不存在或 action 非法。
    """
    company = await company_repository.get_by_company_id(db, company_id)
    if company is None:
        raise BusinessError(code=404, message="企业不存在")

    if action == "pass":
        company.audit_status = "VERIFIED"
        company.audit_reason = None
    elif action == "reject":
        if not reason:
            raise BusinessError(code=400, message="驳回时必须填写原因")
        company.audit_status = "REJECTED"
        company.audit_reason = reason
    else:
        raise BusinessError(code=400, message="无效的审核动作，仅支持 pass / reject")

    company.updated_at = datetime.now()
    await db.flush()

    return CompanyAuditItem(
        id=company.id,
        company_name=company.company_name,
        industry=company.industry,
        scale=company.scale,
        website=company.website,
        description=company.description,
        address=company.address,
        contact_name=company.contact_name,
        contact_phone=company.contact_phone,
        contact_email=company.contact_email,
        audit_status=company.audit_status,
        audit_reason=company.audit_reason,
        created_at=company.created_at,
    )


async def list_operation_logs(
    db: AsyncSession,
    log_type: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    size: int = 20,
) -> PageResult:
    """获取操作日志分页列表。

    Args:
        db: 异步数据库会话。
        log_type: 日志类型筛选。
        keyword: 搜索关键词。
        page: 页码。
        size: 每页条数。

    Returns:
        PageResult: 分页结果，records 为 LogItem 列表。
    """
    logs, total = await operation_log_repository.list_logs(db, log_type, keyword, page, size)

    records = [
        LogItem(
            id=log.id,
            user_id=log.user_id,
            module=log.module,
            action=log.action,
            detail=log.detail,
            ip=log.ip,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return PageResult(records=[r.model_dump(mode="json") for r in records], total=total, page=page, size=size)


async def set_job_status(db: AsyncSession, job_id: int, status: str) -> JobAdminItem:
    """强制设置岗位状态（下架/恢复）。

    Args:
        db: 异步数据库会话。
        job_id: 岗位主键。
        status: 目标状态，CLOSED 或 OPEN。

    Returns:
        JobAdminItem: 更新后的岗位信息。

    Raises:
        BusinessError: 岗位不存在或状态非法。
    """
    job = await job_repository.get_by_id(db, job_id)
    if job is None:
        raise BusinessError(code=404, message="岗位不存在")

    if status not in ("CLOSED", "OPEN"):
        raise BusinessError(code=400, message="无效的状态值，仅支持 CLOSED / OPEN")

    await job_repository.update_job(db, job, {"status": status})
    await db.flush()

    # 获取企业名称
    company_name = None
    company = await company_repository.get_by_company_id(db, job.company_id)
    if company:
        company_name = company.company_name

    return JobAdminItem(
        id=job.id,
        title=job.title,
        company_id=job.company_id,
        company_name=company_name,
        city=job.city,
        status=job.status,
        views=job.views,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


async def list_skill_audit(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
) -> PageResult:
    """获取技能审核列表（CANDIDATE 状态的技能）。"""
    skills, total = await skill_repository.list_candidates(db, page, size)

    records = [
        SkillAuditItem(
            id=s.id,
            name=s.name,
            category=s.category,
            status=s.status,
            created_at=s.created_at,
        )
        for s in skills
    ]

    return PageResult(records=[r.model_dump(mode="json") for r in records], total=total, page=page, size=size)


async def audit_skill(
    db: AsyncSession,
    skill_id: int,
    action: str,
    target_id: int | None = None,
) -> SkillAuditItem:
    """审核候选技能（通过/驳回/合并）。"""
    skill = await skill_repository.get_by_id(db, skill_id)
    if skill is None:
        raise BusinessError(code=404, message="技能不存在")
    if skill.status != "CANDIDATE":
        raise BusinessError(code=400, message="技能不在待审核状态")

    if action == "approve":
        await skill_repository.approve_skill(db, skill_id, target_id=target_id)
    elif action == "reject":
        await skill_repository.reject_skill(db, skill_id)
    else:
        raise BusinessError(code=400, message="无效的审核动作，仅支持 approve / reject")

    return SkillAuditItem(
        id=skill.id,
        name=skill.name,
        category=skill.category,
        status=skill.status,
        created_at=skill.created_at,
    )
