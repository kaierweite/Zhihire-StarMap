"""岗位业务服务模块。

编排岗位的 CRUD、搜索、技能关联等 8 个端点对应的业务逻辑。"""
import json
import os
from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.storage.file_store import file_store
from app.models.entities.job import Job
from app.models.entities.job_skill import JobSkill
from app.models.entities.job_application import JobApplication
from app.models.entities.parse_task import ParseTask
from app.models.entities.upload_file import UploadFile as UploadFileEntity
from app.models.entities.user import User
from app.models.schemas.job import (
    ApplyJobResult,
    AddJobSkillRequest,
    AddJobSkillResult,
    CreateJobRequest,
    CreateJobResult,
    JdParseResult,
    JdUploadResult,
    JobDetail,
    JobItem,
    JobSkillItem,
    UpdateJobRequest,
)
from app.repositories import (
    company_repository,
    job_application_repository,
    job_repository,
    job_skill_repository,
    occupation_role_repository,
    parse_task_repository,
    skill_repository,
    upload_file_repository,
)
from app.services.errors import BusinessError
from app.services.notification_service import send_notification

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_MIME_TYPES: set[str] = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


async def create_job(
    db: AsyncSession,
    user_id: int,
    req: CreateJobRequest,
) -> CreateJobResult:
    company = await company_repository.get_by_user_id(db, user_id)
    if company is None:
        raise BusinessError(403, "企业不存在，无权限发布岗位")
    if company.audit_status != "VERIFIED":
        raise BusinessError(403, "企业未通过审核，无法发布岗位")
    job = Job(
        company_id=company.id,
        occupation_role_id=req.occupation_role_id,
        title=req.title,
        city=req.city,
        education_requirement=req.education_requirement,
        experience_min=req.experience_min,
        salary_min=req.salary_min,
        salary_max=req.salary_max,
        job_type=req.job_type,
        description=req.description,
        is_campus=req.is_campus,
        major=req.major,
        job_category=req.job_category,
        benefits=req.benefits,
    )
    job = await job_repository.create(db, job)
    await db.commit()
    return CreateJobResult(id=job.id, title=job.title)


async def search_jobs(
    db: AsyncSession,
    keyword: str | None = None,
    city: str | None = None,
    education_requirement: str | None = None,
    experience_min: int | None = None,
    salary_min: float | None = None,
    salary_max: float | None = None,
    job_type: str | None = None,
    major: str | None = None,
    job_category: str | None = None,
    company_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[JobItem], int]:
    records, total = await job_repository.search_jobs(
        db, keyword=keyword, city=city,
        education_requirement=education_requirement,
        experience_min=experience_min, salary_min=salary_min,
        salary_max=salary_max, job_type=job_type, company_id=company_id,
        status=status, page=page, size=size,
    )
    company_ids = list({r.company_id for r in records})
    companies = {}
    for cid in company_ids:
        c = await company_repository.get_by_company_id(db, cid)
        if c:
            companies[cid] = c
    items = []
    for r in records:
        comp = companies.get(r.company_id)
        items.append(JobItem(
            id=r.id, company_id=r.company_id,
            company_name=comp.company_name if comp else None,
            industry=comp.industry if comp else None,
            scale=comp.scale if comp else None,
            company_type=comp.company_type if comp else None,
            title=r.title, city=r.city,
            education_requirement=r.education_requirement,
            experience_min=r.experience_min,
            salary_min=float(r.salary_min) if r.salary_min is not None else None,
            salary_max=float(r.salary_max) if r.salary_max is not None else None,
            job_type=r.job_type, status=r.status, views=r.views,
            is_campus=r.is_campus,
            major=r.major,
            job_category=r.job_category,
            benefits=r.benefits, occupation_role_id=r.occupation_role_id,
            created_at=r.created_at, updated_at=r.updated_at,
        ))
    return items, total


async def get_job_detail(
    db: AsyncSession,
    job_id: int,
    increment_view: bool = True,
) -> JobDetail:
    job, company = await job_repository.get_by_id_with_company(db, job_id)
    if job is None or company is None:
        raise BusinessError(404, "岗位不存在")
    if company.audit_status != "VERIFIED":
        raise BusinessError(404, "岗位不存在")
    if increment_view:
        await job_repository.increment_views(db, job.id)
        await db.commit()
        await db.refresh(job)
    role_name = None
    if job.occupation_role_id:
        role = await occupation_role_repository.get_by_id(db, job.occupation_role_id)
        role_name = role.name if role else None
    skills = []
    skill_rows = await job_skill_repository.list_by_job(db, job_id)
    for js, sk in skill_rows:
        skills.append(JobSkillItem(
            id=js.id, job_id=js.job_id, skill_id=js.skill_id,
            skill_name=sk.name, skill_category=sk.category,
            importance=js.importance, required_level=js.required_level,
        ))
    return JobDetail(
        id=job.id, company_id=job.company_id,
        company_name=company.company_name,
        occupation_role_id=job.occupation_role_id,
        occupation_role_name=role_name,
        title=job.title, city=job.city,
        education_requirement=job.education_requirement,
        experience_min=job.experience_min,
        salary_min=float(job.salary_min) if job.salary_min is not None else None,
        salary_max=float(job.salary_max) if job.salary_max is not None else None,
        job_type=job.job_type, description=job.description,
        requirements=job.requirements, source=job.source,
        status=job.status, views=job.views + 1 if increment_view else job.views,
        is_campus=job.is_campus,
        benefits=job.benefits, skills=skills,
        created_at=job.created_at, updated_at=job.updated_at,
    )


async def update_job(
    db: AsyncSession,
    company_id: int,
    job_id: int,
    req: UpdateJobRequest,
) -> JobDetail:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    values: dict[str, Any] = {}
    for field in [
        "title", "city", "education_requirement", "experience_min",
        "salary_min", "salary_max", "job_type", "description",
        "occupation_role_id", "status", "benefits",
    ]:
        val = getattr(req, field, None)
        if val is not None:
            values[field] = val
    await job_repository.update_job(db, job, values)
    await db.commit()
    return await get_job_detail(db, job_id, increment_view=False)


async def delete_job(db: AsyncSession, company_id: int, job_id: int) -> None:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    await job_repository.soft_delete(db, job)
    await db.commit()


async def add_job_skill(
    db: AsyncSession,
    company_id: int,
    job_id: int,
    req: AddJobSkillRequest,
) -> AddJobSkillResult:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    skill = await skill_repository.get_by_id(db, req.skill_id)
    if skill is None:
        raise BusinessError(404, "技能不存在")
    existing = await job_skill_repository.get_by_job_and_skill(db, job_id, req.skill_id)
    if existing:
        raise BusinessError(409, "该技能已关联到此岗位")
    job_skill = JobSkill(job_id=job_id, skill_id=req.skill_id, importance=req.importance, required_level=req.required_level)
    job_skill = await job_skill_repository.create(db, job_skill)
    await db.commit()
    return AddJobSkillResult(id=job_skill.id, job_id=job_id, skill_id=req.skill_id, required_level=req.required_level)


async def list_job_skills(db: AsyncSession, job_id: int) -> list[JobSkillItem]:
    skill_rows = await job_skill_repository.list_by_job(db, job_id)
    items = []
    for js, sk in skill_rows:
        items.append(JobSkillItem(
            id=js.id, job_id=js.job_id, skill_id=js.skill_id,
            skill_name=sk.name, skill_category=sk.category,
            importance=js.importance, required_level=js.required_level,
        ))
    return items


async def remove_job_skill(
    db: AsyncSession, company_id: int, job_id: int, skill_id: int,
) -> None:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    deleted = await job_skill_repository.delete_by_job_and_skill(db, job_id, skill_id)
    if not deleted:
        raise BusinessError(404, "技能关联不存在")
    await db.commit()


async def batch_add_job_skills(
    db: AsyncSession,
    company_id: int,
    job_id: int,
    skills: list[dict],
) -> list[AddJobSkillResult]:
    """批量为岗位添加技能要求。"""
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")

    results: list[AddJobSkillResult] = []
    for skill_data in skills:
        skill_id = skill_data.get("skill_id")
        importance = skill_data.get("importance", 3.0)
        required_level = skill_data.get("required_level", "NICE")

        if skill_id is None:
            continue

        existing = await job_skill_repository.get_by_job_and_skill(db, job_id, skill_id)
        if existing:
            continue

        job_skill = JobSkill(
            job_id=job_id,
            skill_id=skill_id,
            importance=importance,
            required_level=required_level,
        )
        job_skill = await job_skill_repository.create(db, job_skill)
        results.append(AddJobSkillResult(
            id=job_skill.id,
            job_id=job_id,
            skill_id=skill_id,
            required_level=required_level,
        ))

    await db.commit()
    return results


async def apply_job(
    db: AsyncSession, user_id: int, job_id: int, resume_id: int | None = None,
) -> ApplyJobResult:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.status != "OPEN":
        raise BusinessError(404, "岗位不存在或已关闭")
    existing = await job_application_repository.get_by_user_and_job(db, user_id, job_id)
    if existing:
        raise BusinessError(409, "已投递过该岗位")
    application = JobApplication(user_id=user_id, job_id=job_id, resume_id=resume_id)
    application = await job_application_repository.create(db, application)
    await db.commit()

    # Send APPLICATION notification to the company
    try:
        company = await company_repository.get_by_company_id(db, job.company_id)
        if company:
            await send_notification(
                db,
                user_id=company.user_id,
                title="新简历投递",
                type_="APPLICATION",
                content=f"求职者已投递岗位「{job.title}」，请及时查看。",
            )
            await db.commit()
    except Exception:
        pass  # Notifications must never block the main flow
    return ApplyJobResult(id=application.id, user_id=user_id, job_id=job_id, status=application.status)


async def list_job_applications(
    db: AsyncSession, company_id: int, job_id: int, page: int = 1, size: int = 20,
) -> tuple[list, int]:
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")
    rows, total = await job_application_repository.list_by_job_paginated(db, job_id, page=page, size=size)
    items = []
    for app, username, email, phone in rows:
        items.append(ApplyJobResult(id=app.id, job_id=app.job_id, user_id=app.user_id, status=app.status))
    return items, total


async def update_application_status(
    db: AsyncSession, company_id: int, application_id: int, status: str,
) -> dict:
    """企业更新投递状态（ACCEPTED/REJECTED），并发送通知给求职者。"""
    from app.repositories import job_application_repository
    from app.repositories import company_repository

    app = await job_application_repository.get_by_id(db, application_id)
    if app is None:
        raise BusinessError(404, "投递记录不存在")

    job = await job_repository.get_by_id(db, app.job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")

    app.status = status
    await db.flush()

    # Send APPLICATION notification to the candidate
    try:
        company = await company_repository.get_by_company_id(db, company_id)
        company_name = company.company_name if company else ""
        await send_notification(
            db,
            user_id=app.user_id,
            title="投递状态更新",
            type_="APPLICATION",
            content=f"{company_name}已处理您的「{job.title}」投递，状态为：{status}。",
        )
    except Exception:
        pass

    await db.commit()
    return {"id": app.id, "status": app.status}


async def upload_jd(
    db: AsyncSession,
    user: User,
    file: UploadFile,
) -> JdUploadResult:
    """上传 JD 文件。"""
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise BusinessError(400, "文件大小不能超过 10MB")

    mime_type = file.content_type or ""
    if mime_type not in ALLOWED_MIME_TYPES:
        raise BusinessError(400, f"不支持的文件类型: {mime_type}，仅支持 PDF/DOC/DOCX")

    await file.seek(0)

    access_path = await file_store.save(file, subdir="jds")
    stored_name = os.path.basename(access_path)

    upload_entity = UploadFileEntity(
        original_name=file.filename or "untitled",
        stored_name=stored_name,
        path=access_path,
        size=file_size,
        mime_type=mime_type,
        uploader_id=user.id,
    )
    upload_entity = await upload_file_repository.create(db, upload_entity)

    task = ParseTask(
        file_id=upload_entity.id,
        user_id=user.id,
        status="WAITING",
        result=None,
    )
    task = await parse_task_repository.create(db, task)

    await db.commit()

    return JdUploadResult(
        file_id=upload_entity.id,
        task_id=task.id,
        file_name=file.filename or "untitled",
    )


async def get_jd_parse_result(
    db: AsyncSession,
    user: User,
    task_id: int,
) -> JdParseResult:
    """获取 JD 解析结果。"""
    task = await parse_task_repository.get_by_id(db, task_id)
    if task is None:
        raise BusinessError(404, "解析任务不存在")
    if task.user_id != user.id:
        raise BusinessError(403, "无权访问此解析任务")

    result_data = {}
    if task.result:
        if isinstance(task.result, str):
            try:
                result_data = json.loads(task.result)
            except (json.JSONDecodeError, TypeError):
                pass
        elif isinstance(task.result, dict):
            result_data = task.result

    return JdParseResult(
        task_id=task.id,
        status=task.status,
        file_id=task.file_id,
        title=result_data.get("title"),
        city=result_data.get("city"),
        education_requirement=result_data.get("education_requirement"),
        experience_min=result_data.get("experience_min"),
        salary_min=result_data.get("salary_min"),
        salary_max=result_data.get("salary_max"),
        job_type=result_data.get("job_type"),
        description=result_data.get("description"),
        benefits=result_data.get("benefits"),
        skills=result_data.get("skills", []),
        parsed_at=task.updated_at,
    )
