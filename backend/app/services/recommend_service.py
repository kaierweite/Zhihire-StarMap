"""推荐业务服务模块。

编排岗位推荐、推荐反馈、职业规划等业务逻辑。
"""
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.matching import batch_score_jobs
from app.models.entities.recommend_record import RecommendRecord
from app.models.schemas.matching import CareerPathItem, GapSkillItem, RecommendItem
from app.repositories import (
    job_repository,
    job_skill_repository,
    recommend_record_repository,
    resume_repository,
    user_skill_repository,
    occupation_role_repository,
)
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)


async def recommend_jobs_for_user(
    db: AsyncSession,
    user_id: int,
    count: int = 10,
) -> list[dict[str, Any]]:
    """为当前用户推荐岗位。

    基于用户的技能与所有 OPEN 岗位进行匹配，然后返回 Top-N 推荐。
    同时缓存推荐记录到 recommend_record 表。

    Args:
        db: 数据库会话。
        user_id: 用户主键。
        count: 推荐岗位数量。

    Returns:
        list[dict]: 推荐结果列表。
    """
    # 1. 获取用户技能
    user_skill_rows = await user_skill_repository.list_by_user(db, user_id)
    user_skills: dict[int, float] = {}
    for us, sk in user_skill_rows:
        user_skills[sk.id] = us.proficiency_level

    if not user_skills:
        return []

    # 2. 获取所有 OPEN 岗位
    search_results, total = await job_repository.search_jobs(db, status="OPEN", page=1, size=200)
    if not search_results:
        return []

    # 3. 获取岗位技能要求
    job_skills_map: dict[int, dict[int, str]] = {}
    for job in search_results:
        skill_rows = await job_skill_repository.list_by_job(db, job.id)
        job_skills: dict[int, str] = {}
        for js, sk in skill_rows:
            job_skills[sk.id] = js.required_level
        if job_skills:  # 只推荐有技能要求的岗位（有匹配基础）
            job_skills_map[job.id] = job_skills

    if not job_skills_map:
        return []

    # 4. 计算匹配
    matched = batch_score_jobs(user_skills, job_skills_map)

    # 5. 取 Top-N
    top_matched = matched[:count]

    # 6. 筛选未被推荐过的岗位
    results: list[dict[str, Any]] = []
    new_records: list[RecommendRecord] = []

    for m in top_matched:
        job_id = m["job_id"]
        existing = await recommend_record_repository.get_by_user_and_job(db, user_id, job_id)
        if existing:
            continue

        score = m["score"]
        job_obj = next((j for j in search_results if j.id == job_id), None)
        job_title = job_obj.title if job_obj else None

        results.append({
            "id": job_id,
            "job_id": job_id,
            "job_title": job_title,
            "score": score,
        })

        new_records.append(RecommendRecord(
            user_id=user_id,
            job_id=job_id,
            score=score,
        ))

    # 7. 批量保存推荐记录
    if new_records:
        await recommend_record_repository.batch_create(db, new_records)
        await db.commit()

    return results


async def get_recommendations(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    size: int = 20,
) -> tuple[list[RecommendItem], int]:
    """查询用户的推荐记录列表。

    Args:
        db: 数据库会话。
        user_id: 用户主键。
        page: 页码。
        size: 每页条数。

    Returns:
        tuple[list[RecommendItem], int]: (推荐列表, 总数)。
    """
    records, total = await recommend_record_repository.list_by_user(db, user_id, page, size)

    items = []
    for r in records:
        job = await job_repository.get_by_id(db, r.job_id)
        job_title = job.title if job else None
        company = None
        if job:
            from app.repositories import company_repository
            c = await company_repository.get_by_company_id(db, job.company_id)
            company = c.company_name if c else None

        items.append(RecommendItem(
            id=r.id,
            job_id=r.job_id,
            job_title=job_title,
            company_name=company,
            score=r.score,
            is_clicked=r.is_clicked,
            is_applied=r.is_applied,
            created_at=r.created_at,
        ))

    return items, total


async def mark_recommendation_action(
    db: AsyncSession,
    user_id: int,
    record_id: int,
    action: str,
) -> bool:
    """标记推荐记录的操作状态（点击或投递）。

    Args:
        db: 数据库会话。
        user_id: 用户主键。
        record_id: 推荐记录主键。
        action: 操作类型："click" 或 "apply"。

    Returns:
        bool: 操作是否成功。
    """
    record = await recommend_record_repository.get_by_id(db, record_id)
    if record is None or record.user_id != user_id:
        raise BusinessError(404, "推荐记录不存在")

    if action == "click":
        result = await recommend_record_repository.mark_clicked(db, record_id)
    elif action == "apply":
        result = await recommend_record_repository.mark_applied(db, record_id)
    else:
        raise BusinessError(400, "不支持的操作类型")

    await db.commit()
    return result


async def recommend_career_paths(
    db: AsyncSession,
    user_id: int,
    top_n: int = 5,
) -> list[CareerPathItem]:
    """基于用户技能推荐职业发展路径。

    通过用户技能与各职业角色的技能要求进行匹配，找出最匹配的职业方向。

    Args:
        db: 数据库会话。
        user_id: 用户主键。
        top_n: 推荐路径数量。

    Returns:
        list[CareerPathItem]: 职业路径推荐列表。
    """
    # 1. 获取用户技能
    user_skill_rows = await user_skill_repository.list_by_user(db, user_id)
    user_skill_ids = {sk.id for _, sk in user_skill_rows}
    user_skills: dict[int, float] = {}
    for us, sk in user_skill_rows:
        user_skills[sk.id] = us.proficiency_level

    if not user_skills:
        return []

    # 2. 获取所有职业角色
    from app.repositories import role_skill_repository
    roles = await occupation_role_repository.list_all(db)
    if not roles:
        return []

    # 3. 构建角色技能映射
    role_skills_map: dict[int, dict[int, str]] = {}
    role_names: dict[int, str] = {}
    for role in roles:
        role_skill_rows = await role_skill_repository.list_by_role(db, role.id)
        skill_map: dict[int, str] = {}
        for rs, sk in role_skill_rows:
            skill_map[sk.id] = rs.requirement_level
        if skill_map:
            role_skills_map[role.id] = skill_map
            role_names[role.id] = role.name

    if not role_skills_map:
        return []

    # 4. 计算匹配
    matched = batch_score_jobs(user_skills, role_skills_map)

    # 5. 构建结果
    paths: list[CareerPathItem] = []
    for m in matched[:top_n]:
        role_id = m["job_id"]  # batch_score_jobs 的 job_id 字段存储的是 role_id
        role_name = role_names.get(role_id, f"role_{role_id}")

        # 获取角色技能的详细信息
        role_skill_rows = await role_skill_repository.list_by_role(db, role_id)
        gap_skills = []
        for rs, sk in role_skill_rows:
            if sk.id not in user_skill_ids:
                gap_skills.append(GapSkillItem(
                    skill_name=sk.name,
                    requirement_level=rs.requirement_level,
                ))

        paths.append(CareerPathItem(
            role_id=role_id,
            role_name=role_name,
            score=m["score"],
            gap_skills=gap_skills,
        ))

    return paths
