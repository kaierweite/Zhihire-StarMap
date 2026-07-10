"""匹配推荐业务服务模块。

编排三层匹配算法（召回→打分→图谱增值）、懒计算+新鲜度缓存、
双向推荐（求职端/企业端）、投递和邀请业务逻辑。
"""
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.matching.recall import recall_candidates_for_job, recall_jobs_for_user
from app.core.matching.scorer import compute_breakdown
from app.core.matching.graph_boost import compute_graph_boost
from app.core.matching.rationale_builder import build_rationale
from app.models.entities.job import Job
from app.models.entities.job_skill import JobSkill
from app.models.entities.recommend_record import RecommendRecord
from app.models.entities.resume import Resume
from app.models.entities.skill import Skill
from app.models.entities.skill_relation import SkillRelation
from app.models.entities.user import User
from app.models.entities.user_profile import UserProfile
from app.models.entities.user_skill import UserSkill
from app.repositories import (
    company_repository,
    job_application_repository,
    job_repository,
    job_skill_repository,
    skill_relation_repository,
    skill_repository,
    user_skill_repository,
)
from app.repositories.match_repository import match_repository as match_repo
from app.repositories.recommend_repository import recommend_repository as recommend_repo
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)

# 外部导入（避免循环引用，仅函数级导入）
from app.services import job_service  # noqa: E402


async def _get_user_profile(db: AsyncSession, user_id: int) -> UserProfile | None:
    """获取用户档案。"""
    stmt = select(UserProfile).where(
        UserProfile.user_id == user_id,
        UserProfile.deleted_at == "0",
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _get_skill_relation_map(
    db: AsyncSession, skill_ids: set[int],
) -> dict[int, dict[str, list[int]]]:
    """获取技能关系映射。"""
    rows = await skill_relation_repository.list_by_skill_ids(db, list(skill_ids))
    relation_map: dict[int, dict[str, list[int]]] = {}
    for sr in rows:
        if sr.skill_id not in relation_map:
            relation_map[sr.skill_id] = {}
        rel_type = sr.relation_type
        if rel_type not in relation_map[sr.skill_id]:
            relation_map[sr.skill_id][rel_type] = []
        relation_map[sr.skill_id][rel_type].append(sr.related_skill_id)
    return relation_map


async def _get_skill_names(db: AsyncSession, skill_ids: set[int]) -> dict[int, str]:
    """查询技能名称映射。"""
    names: dict[int, str] = {}
    for sid in skill_ids:
        skill = await skill_repository.get_by_id(db, sid)
        if skill:
            names[sid] = skill.name
    return names


async def _compute_match(
    db: AsyncSession,
    user_id: int,
    resume_id: int,
    job_id: int,
) -> dict[str, Any]:
    """三层匹配算法：召回→维度打分→图谱增值。

    1. 获取用户技能、学历、经验、城市数据
    2. 获取岗位技能要求及元信息
    3. 四维度打分
    4. 图谱增值 + 可解释拼接
    5. 计算总分
    6. 缓存到 match_result

    Returns:
        dict: {"score": float, "match_detail": {...}}
    """
    # 1. 用户技能
    user_skill_rows = await user_skill_repository.list_by_user(db, user_id)
    user_skills: dict[int, float] = {}
    user_skill_ids: set[int] = set()
    for us, sk in user_skill_rows:
        user_skills[sk.id] = us.proficiency_level
        user_skill_ids.add(sk.id)

    # 2. 用户档案（学历、经验、城市）
    profile = await _get_user_profile(db, user_id)
    user_edu = profile.education if profile else None
    user_exp_years = float(profile.work_years) if profile and profile.work_years else None
    user_city = profile.current_city or profile.expected_city if profile else None

    # 3. 岗位技能要求
    job_skill_rows = await job_skill_repository.list_by_job(db, job_id)
    job_skills: dict[int, str] = {}
    skill_importances: dict[int, float] = {}
    all_skill_ids: set[int] = set()
    for js, sk in job_skill_rows:
        job_skills[sk.id] = js.required_level
        skill_importances[sk.id] = js.importance
        all_skill_ids.add(sk.id)

    # 4. 岗位信息（学历/经验/城市要求）
    job = await job_repository.get_by_id(db, job_id)
    if job is None:
        raise BusinessError(404, "岗位不存在")

    # 5. 四维度打分
    breakdown_result = compute_breakdown(
        user_skills=user_skills,
        job_skills=job_skills,
        skill_importances=skill_importances,
        user_edu=user_edu,
        job_edu=job.education_requirement,
        user_exp_years=user_exp_years,
        job_exp_min=job.experience_min,
        user_city=user_city,
        job_city=job.city,
    )

    # 6. 图谱增值
    relation_map = await _get_skill_relation_map(db, all_skill_ids)
    skill_names = await _get_skill_names(db, all_skill_ids)
    graph_result = compute_graph_boost(user_skill_ids, set(job_skills.keys()), relation_map, skill_names)

    # 7. 总分：主分 * (1 + boost)
    base_score = breakdown_result["score"]
    boost = graph_result["boost"]
    total_score = min(base_score * (1.0 + boost), 100.0)

    # 8. 可解释拼接
    rationale = build_rationale(breakdown_result["breakdown"], graph_result["hints"])

    # 9. 构建 match_detail JSONB
    match_detail = {
        "score": round(total_score, 2),
        "breakdown": breakdown_result["breakdown"],
        "rationale": rationale,
        "graph_hints": graph_result["hints"],
    }

    # 10. 缓存到库
    await match_repo.upsert(db, resume_id, job_id, round(total_score, 2), match_detail)

    return {
        "score": round(total_score, 2),
        "match_detail": match_detail,
    }


async def get_job_recommendations(
    db: AsyncSession,
    user_id: int,
) -> list[dict[str, Any]]:
    """求职者查看推荐岗位（懒计算 + 新鲜度缓存）。

    Args:
        db: 数据库会话。
        user_id: 用户主键。

    Returns:
        list[dict]: 按分数降序排列的推荐结果。
    """
    # 1. 召回候选岗位
    candidates = await recall_jobs_for_user(db, user_id)
    if not candidates:
        return []

    # 2. 逐对检查 match_result 缓存
    results: list[dict[str, Any]] = []
    for cand in candidates:
        resume_id = cand["resume_id"]
        job_id = cand["job_id"]

        # 懒检查
        existing = await match_repo.get_by_resume_and_job(db, resume_id, job_id)
        if existing and not existing.is_stale:
            # 缓存命中且未过期
            result = {
                "job_id": job_id,
                "resume_id": resume_id,
                "score": existing.score,
                "match_detail": existing.match_detail,
            }
        else:
            # 缺失或过期 → 重算
            result = await _compute_match(db, user_id, resume_id, job_id)
            result["resume_id"] = resume_id
            result["job_id"] = job_id

        # 补充岗位外显信息
        job = await job_repository.get_by_id(db, job_id)
        if job:
            result["title"] = job.title
            company = await company_repository.get_by_company_id(db, job.company_id)
            result["company_name"] = company.company_name if company else None

        # 记录推荐（去重）
        existing_rec = await recommend_repo.get_by_user_and_job(db, user_id, job_id)
        if not existing_rec:
            await recommend_repo.create(db, RecommendRecord(
                user_id=user_id,
                job_id=job_id,
                score=result.get("score", 0),
                recommend_type="JOB",
            ))

        results.append(result)

    await db.commit()
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results


async def get_candidate_recommendations(
    db: AsyncSession,
    company_id: int,
    job_id: int,
) -> list[dict[str, Any]]:
    """企业查看某岗位的候选人推荐（懒计算 + 缓存复用）。

    Args:
        db: 数据库会话。
        company_id: 企业主键（鉴权）。
        job_id: 岗位主键。

    Returns:
        list[dict]: 按分数降序排列的候选人列表。
    """
    # 1. 鉴权
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")

    # 2. 召回候选人
    candidates = await recall_candidates_for_job(db, job_id)
    if not candidates:
        return []

    results: list[dict[str, Any]] = []
    for cand in candidates:
        resume_id = cand["resume_id"]
        cand_user_id = cand["user_id"]

        # 懒检查 match_result（双向共用同一条记录）
        existing = await match_repo.get_by_resume_and_job(db, resume_id, job_id)
        if existing and not existing.is_stale:
            result = {
                "job_id": job_id,
                "resume_id": resume_id,
                "user_id": cand_user_id,
                "score": existing.score,
                "match_detail": existing.match_detail,
            }
        else:
            result = await _compute_match(db, cand_user_id, resume_id, job_id)
            result["resume_id"] = resume_id
            result["job_id"] = job_id
            result["user_id"] = cand_user_id

        # 获取用户基本信息
        from app.repositories import user_repository
        user = await user_repository.get_by_id(db, cand_user_id)
        result["name"] = user.real_name or user.username if user else None

        # 记录企业端推荐
        existing_rec = await recommend_repo.get_by_user_and_job(db, cand_user_id, job_id)
        if not existing_rec:
            await recommend_repo.upsert_talent_recommend(db, cand_user_id, resume_id, job_id, result.get("score", 0))

        results.append(result)

    await db.commit()
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results


async def apply_job(
    db: AsyncSession,
    user_id: int,
    job_id: int,
    resume_id: int,
) -> dict[str, Any]:
    """求职者投递岗位。

    复用已有 job_service.apply_job 逻辑，同时标记推荐记录。
    """
    # 1. 委托已有投递逻辑
    apply_result = await job_service.apply_job(db, user_id, job_id, resume_id)

    # 2. 标记推荐记录
    rec = await recommend_repo.get_by_user_and_job(db, user_id, job_id)
    if rec:
        await recommend_repo.mark_applied(db, rec.id)

    # 3. TODO: 发送通知 notification(type=APPLICATION)
    await db.commit()

    return {
        "application_id": apply_result.id,
        "status": apply_result.status,
    }


async def invite_candidate(
    db: AsyncSession,
    company_id: int,
    job_id: int,
    resume_id: int,
) -> dict[str, Any]:
    """企业邀请候选人面试。

    Args:
        db: 数据库会话。
        company_id: 企业主键（鉴权）。
        job_id: 岗位主键。
        resume_id: 候选人简历主键。

    Returns:
        dict: 邀请结果。
    """
    # 1. 鉴权
    job = await job_repository.get_by_id(db, job_id)
    if job is None or job.company_id != company_id:
        raise BusinessError(404, "岗位不存在")

    # 2. 查简历所属用户
    stmt = select(Resume).where(Resume.id == resume_id, Resume.deleted_at == "0")
    result = await db.execute(stmt)
    resume = result.scalar_one_or_none()
    if resume is None:
        raise BusinessError(404, "简历不存在")

    # 3. 创建或更新推荐记录（企业端）
    rec = await recommend_repo.upsert_talent_recommend(
        db, resume.user_id, resume_id, job_id, 0,
    )
    await recommend_repo.mark_invited(db, rec.id)

    # 4. TODO: 发送通知 notification(type=INTERVIEW_INVITE)
    await db.commit()

    return {
        "record_id": rec.id,
        "user_id": resume.user_id,
        "status": "invited",
    }
