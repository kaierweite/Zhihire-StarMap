"""职业规划业务服务模块。

编排核心算法（缺口分析 + 学习路径规划 + 图谱提示），
调用仓储层持久化规划结果，末句经 LLM 润色。
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.career.gap_analyzer import analyze_skill_gap, compute_match_score
from app.core.career.planner import build_learning_path, build_rationale, generate_graph_hints
from app.infrastructure.llm.deepseek_client import deepseek_client
from app.models.entities.career_plan import CareerPlan
from app.models.schemas.career import CareerPlanResponse
from app.repositories import career_repository, role_repository, role_skill_repository, \
    skill_relation_repository, skill_repository, user_skill_repository
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)


async def generate_plan(
    db: AsyncSession,
    user_id: int,
    target_role_id: int,
    source: str = "PROACTIVE",
) -> CareerPlanResponse:
    """为指定用户生成对目标角色的职业规划。

    算法流程（分数/路径不经大模型）：
    1. 取角色 MUST/NICE/BONUS 技能集 - 用户已有技能 = gap_skills
    2. 对 gap_skills 沿 PREREQUISITE 边做拓扑排序 -> learning_path
    3. 附加 graph_hints：SIMILAR / COMPLEMENTARY 关联提示
    4. 计算匹配分数
    5. rationale 模板拼接 + LLM 末句润色
    6. 写入/更新 career_plan -> 返回结果

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。
        target_role_id: 目标角色主键。
        source: 规划来源，默认 PROACTIVE。

    Returns:
        CareerPlanResponse: 完整的职业规划结果。

    Raises:
        BusinessError: 角色不存在或未配置技能时抛出。
    """
    # 1. 校验角色存在
    role = await role_repository.get_by_id(db, target_role_id)
    if role is None:
        raise BusinessError(404, "目标角色不存在")

    # 2. 获取用户技能
    user_skills = await user_skill_repository.list_by_user(db, user_id)
    user_skill_ids = {us.skill_id for us, _ in user_skills}
    user_skill_names = {sk.name for _, sk in user_skills}

    # 3. 获取角色技能要求
    role_skills = await role_skill_repository.list_by_role(db, target_role_id)
    role_skill_map: dict[int, str] = {}
    role_skill_ids: set[int] = set()
    skill_names: dict[int, str] = {}
    for rs, sk in role_skills:
        role_skill_map[sk.id] = rs.requirement_level
        role_skill_ids.add(sk.id)
        skill_names[sk.id] = sk.name

    if not role_skill_ids:
        raise BusinessError(400, f"角色「{role.name}」尚未配置技能要求")

    # 4. 缺口分析
    gap_skills = analyze_skill_gap(user_skill_ids, role_skill_map, skill_names)
    gap_skill_ids = []
    for gs in gap_skills:
        for sid, name in skill_names.items():
            if name == gs.skill_name:
                gap_skill_ids.append(sid)
                break

    # 5. 获取全部技能与关系数据用于拓扑排序
    all_skills_list = await skill_repository.list_active(db)
    all_skills: dict[int, str] = {sk.id: sk.name for sk in all_skills_list}

    all_relations_raw = await skill_relation_repository.list_active(db)
    relations: list[tuple[int, int, str]] = [
        (r.skill_id_a, r.skill_id_b, r.relation_type) for r in all_relations_raw
    ]

    # 6. 构建学习路径（纯算法，不经大模型）
    learning_path = build_learning_path(gap_skill_ids, all_skills, relations)

    # 7. 图谱提示
    graph_hints = generate_graph_hints(gap_skill_ids, all_skills, relations, user_skill_names)

    # 8. 匹配分数（纯算法）
    score = compute_match_score(user_skill_ids, role_skill_ids, role_skill_map)

    # 9. rationale 模板拼接 + LLM 末句润色
    llm_polish = await _polish_rationale(role.name, score, len(gap_skills))
    rationale = build_rationale(role.name, score, len(gap_skills), llm_polish)

    # 10. 构建响应
    response = CareerPlanResponse(
        target_role=role.name,
        gap_skills=[{"skill_name": g.skill_name, "requirement_level": g.requirement_level} for g in gap_skills],
        learning_path=[{"skills": p} for p in learning_path],
        graph_hints=graph_hints,
        rationale=rationale,
        score=score,
        source=source,
    )

    # 11. 持久化（plan_content 为 JSONB，直接存 dict）
    plan = CareerPlan(
        user_id=user_id,
        target_role=role.name,
        target_role_id=target_role_id,
        plan_content=response.model_dump(),
        source=source,
    )
    await career_repository.upsert(db, plan)
    await db.commit()

    logger.info("Career plan generated for user_id=%s role_id=%s source=%s", user_id, target_role_id, source)
    return response


async def get_plan(db: AsyncSession, user_id: int) -> CareerPlan | None:
    """获取某用户最新生成的职业规划记录。

    Args:
        db: 异步数据库会话。
        user_id: 用户主键。

    Returns:
        CareerPlan | None: 规划记录（含原始 JSONB），或 None。
    """
    return await career_repository.get_by_user(db, user_id)


async def _polish_rationale(role_name: str, score: float, gap_count: int) -> str:
    """调用 LLM 对规划说明末句进行润色。

    API key 不存在时返回空字符串（跳过润色）。

    Args:
        role_name: 目标角色名。
        score: 匹配分数。
        gap_count: 缺口数。

    Returns:
        str: LLM 润色后的末句，或空字符串。
    """
    try:
        prompt = (
            f"用户技能与目标岗位「{role_name}」的匹配度为{score}%，"
            f"存在{gap_count}项技能缺口。请用一句话给出学习建议，"
            f"语气积极、专业，不超过30字。"
        )
        messages = [{"role": "user", "content": prompt}]
        result = await deepseek_client.chat(messages)
        return result.strip()
    except Exception:
        logger.warning("LLM polish failed, skipping", exc_info=True)
        return ""