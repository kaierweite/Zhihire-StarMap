"""匹配推荐业务服务模块。

编排匹配计算、结果缓存、技能差距分析等业务逻辑。
"""
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.matching import batch_score_jobs, calculate_skill_gap
from app.models.entities.job import Job
from app.models.entities.resume import Resume
from app.models.schemas.matching import (
    GapSkillItem,
    MatchResultItem,
    SkillGapAnalysis,
    SkillMatchDetail,
)
from app.repositories import (
    job_repository,
    job_skill_repository,
    match_result_repository,
    resume_repository,
    skill_repository,
    user_skill_repository,
)
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)


async def match_resume_to_jobs(
    db: AsyncSession,
    user_id: int,
    resume_id: int,
    job_ids: list[int] | None = None,
) -> list[dict[str, Any]]:
    """执行简历与岗位的匹配分析并缓存结果。

    Args:
        db: 数据库会话。
        user_id: 用户主键（用于鉴权）。
        resume_id: 简历主键。
        job_ids: 投递岗位 ID 列表；None 则匹配所有 OPEN 岗位。

    Returns:
        list[dict]: 匹配结果列表，按分降序。
    """
    # 1. 验证简历归属
    resume = await resume_repository.get_by_id(db, resume_id)
    if resume is None or resume.user_id != user_id:
        raise BusinessError(404, "简历不存在")
    if resume.status != "NORMAL":
        raise BusinessError(400, "简历状态异常，无法匹配")

    # 2. 获取用户技能
    user_skill_rows = await user_skill_repository.list_by_user(db, user_id)
    user_skills: dict[int, float] = {}
    for us, sk in user_skill_rows:
        user_skills[sk.id] = us.proficiency_level

    # 3. 确定目标岗位
    if job_ids:
        target_jobs = []
        for jid in job_ids:
            job = await job_repository.get_by_id(db, jid)
            if job and job.status == "OPEN":
                target_jobs.append(job)
    else:
        search_results, _ = await job_repository.search_jobs(db, status="OPEN", page=1, size=200)
        target_jobs = search_results

    if not target_jobs:
        return []

    # 4. 获取岗位技能要求
    job_skills_map: dict[int, dict[int, str]] = {}
    all_skill_ids: set[int] = set()
    for job in target_jobs:
        skill_rows = await job_skill_repository.list_by_job(db, job.id)
        job_skills: dict[int, str] = {}
        for js, sk in skill_rows:
            job_skills[sk.id] = js.required_level
            all_skill_ids.add(sk.id)
        job_skills_map[job.id] = job_skills

    # 5. 计算匹配
    matched_jobs = batch_score_jobs(user_skills, job_skills_map)

    # 6. 缓存匹配结果
    results = []
    for mj in matched_jobs:
        job_id = mj["job_id"]
        score = mj["score"]
        detail = mj["match_detail"]

        await match_result_repository.upsert(db, resume_id, job_id, score, detail)

        job_obj = next((j for j in target_jobs if j.id == job_id), None)
        results.append({
            "job_id": job_id,
            "job_title": job_obj.title if job_obj else None,
            "score": score,
            "match_detail": detail,
        })

    await db.commit()
    return results


async def get_matched_jobs_for_resume(
    db: AsyncSession,
    user_id: int,
    resume_id: int,
    page: int = 1,
    size: int = 20,
    min_score: float | None = None,
) -> tuple[list[MatchResultItem], int]:
    """查询某简历的匹配结果列表。

    Args:
        db: 数据库会话。
        user_id: 用户主键（鉴权）。
        resume_id: 简历主键。
        page: 页码。
        size: 每页条数。
        min_score: 最低匹配分过滤。

    Returns:
        tuple[list[MatchResultItem], int]: (结果列表, 总数)。
    """
    resume = await resume_repository.get_by_id(db, resume_id)
    if resume is None or resume.user_id != user_id:
        raise BusinessError(404, "简历不存在")

    records, total = await match_result_repository.list_by_resume(db, resume_id, page, size)

    if min_score is not None:
        records = [r for r in records if r.score >= min_score]
        total = len(records)

    items = []
    for r in records:
        job = await job_repository.get_by_id(db, r.job_id)
        job_title = job.title if job else None
        items.append(MatchResultItem(
            id=r.id,
            resume_id=r.resume_id,
            job_id=r.job_id,
            job_title=job_title,
            score=r.score,
            match_detail=r.match_detail,
            created_at=r.created_at,
            updated_at=r.updated_at,
        ))

    return items, total


async def analyze_skill_gap_for_job(
    db: AsyncSession,
    user_id: int,
    job_id: int,
) -> SkillGapAnalysis:
    """分析用户与某个岗位之间的技能差距。

    Args:
        db: 数据库会话。
        user_id: 用户主键。
        job_id: 岗位主键。

    Returns:
        SkillGapAnalysis: 技能差距分析结果。
    """
    # 1. 验证岗位
    job = await job_repository.get_by_id(db, job_id)
    if job is None:
        raise BusinessError(404, "岗位不存在")

    # 2. 获取用户技能
    user_skill_rows = await user_skill_repository.list_by_user(db, user_id)
    user_skill_ids = {sk.id for _, sk in user_skill_rows}

    # 3. 获取岗位技能要求及名称
    skill_rows = await job_skill_repository.list_by_job(db, job_id)
    job_skills: dict[int, str] = {}
    skill_names: dict[int, str] = {}
    for js, sk in skill_rows:
        job_skills[sk.id] = js.required_level
        skill_names[sk.id] = sk.name

    # 4. 计算差距
    gap = calculate_skill_gap(user_skill_ids, job_skills, skill_names)

    return SkillGapAnalysis(
        total_required=gap["total_required"],
        matching_skills=gap["matching_skills"],
        gap_skills=[GapSkillItem(**gs) for gs in gap["gap_skills"]],
        match_rate=gap["match_rate"],
        suggestions=gap["suggestions"],
    )


async def get_single_match_detail(
    db: AsyncSession,
    user_id: int,
    resume_id: int,
    job_id: int,
) -> MatchResultItem:
    """查询某简历与某岗位的单个匹配明细。

    Args:
        db: 数据库会话。
        user_id: 用户主键（鉴权）。
        resume_id: 简历主键。
        job_id: 岗位主键。

    Returns:
        MatchResultItem: 匹配详情。
    """
    resume = await resume_repository.get_by_id(db, resume_id)
    if resume is None or resume.user_id != user_id:
        raise BusinessError(404, "简历不存在")

    job = await job_repository.get_by_id(db, job_id)
    if job is None:
        raise BusinessError(404, "岗位不存在")

    result = await match_result_repository.get_by_resume_and_job(db, resume_id, job_id)
    if result is None:
        raise BusinessError(404, "匹配结果不存在，请先执行匹配分析")

    return MatchResultItem(
        id=result.id,
        resume_id=result.resume_id,
        job_id=result.job_id,
        job_title=job.title,
        score=result.score,
        match_detail=result.match_detail,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
