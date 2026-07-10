"""召回层：SQL 查询扩充候选集。

通过技能交集缩小匹配范围，输出候选 (resume_id, job_id) 对。
每端最多返回 50 对，避免全量笛卡尔积。
"""
import logging
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.job import Job
from app.models.entities.resume import Resume
from app.models.entities.user_skill import UserSkill
from app.models.entities.job_skill import JobSkill

logger = logging.getLogger(__name__)

MAX_CANDIDATES = 50


async def recall_jobs_for_user(
    db: AsyncSession,
    user_id: int,
) -> list[dict[str, Any]]:
    """为求职者召回候选岗位。

    策略：
    1. 获取用户简历和技能
    2. 按有技能交集的 OPEN 岗位召回
    3. 限制 MAX_CANDIDATES 个

    Returns:
        list[dict]: [{resume_id, job_id}] 候选对。
    """
    # 1. 获取用户正常简历
    stmt_resume = select(Resume).where(
        Resume.user_id == user_id,
        Resume.deleted_at == "0",
        Resume.status == "NORMAL",
    )
    result = await db.execute(stmt_resume)
    resumes = list(result.scalars().all())
    if not resumes:
        return []

    # 2. 获取用户技能 ID 集合
    stmt_us = select(UserSkill.skill_id).where(
        UserSkill.user_id == user_id,
        UserSkill.deleted_at == "0",
    )
    result = await db.execute(stmt_us)
    skill_ids = {row[0] for row in result.all()}
    if not skill_ids:
        return []

    # 3. 按技能交集召回 OPEN 岗位
    stmt_job_skill = (
        select(JobSkill.job_id)
        .where(
            JobSkill.skill_id.in_(skill_ids),
            JobSkill.deleted_at == "0",
        )
        .distinct()
        .limit(MAX_CANDIDATES)
    )
    result = await db.execute(stmt_job_skill)
    job_ids = [row[0] for row in result.all()]

    # 4. 验证岗位为 OPEN 状态
    if job_ids:
        stmt_job = select(Job.id).where(
            Job.id.in_(job_ids),
            Job.deleted_at == "0",
            Job.status == "OPEN",
        )
        result = await db.execute(stmt_job)
        valid_ids = {row[0] for row in result.all()}
        job_ids = [jid for jid in job_ids if jid in valid_ids]

    candidates = [
        {"resume_id": resumes[0].id, "job_id": jid}
        for jid in job_ids
    ]
    return candidates[:MAX_CANDIDATES]


async def recall_candidates_for_job(
    db: AsyncSession,
    job_id: int,
) -> list[dict[str, Any]]:
    """为企业召回岗位的候选人。

    策略：
    1. 获取岗位技能要求
    2. 按技能交集召回用户
    3. 限制 MAX_CANDIDATES 个

    Returns:
        list[dict]: [{resume_id, job_id, user_id}] 候选对。
    """
    # 1. 验证岗位存在且 OPEN
    stmt_job = select(Job).where(
        Job.id == job_id,
        Job.deleted_at == "0",
        Job.status == "OPEN",
    )
    result = await db.execute(stmt_job)
    job = result.scalar_one_or_none()
    if job is None:
        return []

    # 2. 获取岗位技能
    stmt_js = select(JobSkill.skill_id).where(
        JobSkill.job_id == job_id,
        JobSkill.deleted_at == "0",
    )
    result = await db.execute(stmt_js)
    skill_ids = {row[0] for row in result.all()}
    if not skill_ids:
        return []

    # 3. 按技能交集召回用户
    stmt_us = (
        select(UserSkill.user_id)
        .where(
            UserSkill.skill_id.in_(skill_ids),
            UserSkill.deleted_at == "0",
        )
        .distinct()
        .limit(MAX_CANDIDATES)
    )
    result = await db.execute(stmt_us)
    user_ids = {row[0] for row in result.all()}

    # 4. 查这些用户的 NORMAL 简历
    candidates = []
    for uid in user_ids:
        stmt_resume = select(Resume).where(
            Resume.user_id == uid,
            Resume.deleted_at == "0",
            Resume.status == "NORMAL",
        )
        result = await db.execute(stmt_resume)
        resume = result.scalar_one_or_none()
        if resume:
            candidates.append({
                "resume_id": resume.id,
                "job_id": job_id,
                "user_id": uid,
            })

    return candidates[:MAX_CANDIDATES]
