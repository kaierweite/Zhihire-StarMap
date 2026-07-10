"""增强匹配算法模块。

在基础 matcher 之上提供更丰富的匹配功能：
- 技能关系感知匹配（利用 SIMILAR / PREREQUISITE 关系补偿）
- 岗位批量评分
- 匹配结果排序与阈值筛选
"""
import math
import logging
from typing import Any

from app.core.matching.matcher import (
    composite_match_score,
    jaccard_similarity,
    match_user_to_job,
    weighted_skill_match,
)

logger = logging.getLogger(__name__)


# 技能要求级别的权重映射
REQUIRED_LEVEL_WEIGHTS: dict[str, float] = {
    "MUST": 1.0,
    "NICE": 0.6,
    "BONUS": 0.3,
}

# 技能关系补偿权重
RELATION_COMPENSATION: dict[str, float] = {
    "SIMILAR": 0.7,        # 相似技能补偿 70%
    "PREREQUISITE": 0.3,   # 先修技能补偿 30%
    "COMPLEMENTARY": 0.5,  # 互补技能补偿 50%
}


def calculate_relation_compensation(
    user_skill_ids: set[int],
    job_skill_ids: set[int],
    relation_map: dict[int, dict[str, list[int]]],
) -> float:
    """计算技能关系补偿分。

    当用户不具备岗位要求的某项技能时，检查是否拥有与该技能
    存在 SIMILAR / PREREQUISITE / COMPLEMENTARY 关系的技能来部分补偿。

    Args:
        user_skill_ids: 用户拥有的技能 ID 集合。
        job_skill_ids: 岗位要求的技能 ID 集合。
        relation_map: skill_id -> {relation_type: [related_skill_ids]}。

    Returns:
        float: 关系补偿分（0.0 ~ 1.0 之间）。
    """
    if not job_skill_ids:
        return 0.0

    missing = job_skill_ids - user_skill_ids
    if not missing:
        return 0.0

    total_compensation = 0.0
    for missing_skill_id in missing:
        relations = relation_map.get(missing_skill_id, {})
        max_comp = 0.0
        for rel_type, related_ids in relations.items():
            weight = RELATION_COMPENSATION.get(rel_type, 0.0)
            overlap = len(set(related_ids) & user_skill_ids)
            if overlap > 0:
                comp = weight * min(overlap / len(related_ids), 1.0)
                max_comp = max(max_comp, comp)
        total_compensation += max_comp

    return total_compensation / len(missing)


def batch_score_jobs(
    user_skills: dict[int, float],
    job_skills_map: dict[int, dict[int, str]],
    relation_map: dict[int, dict[str, list[int]]] | None = None,
    required_threshold: float = 0.3,
) -> list[dict[str, Any]]:
    """批量计算用户与多个岗位的匹配分。

    Args:
        user_skills: user_id -> proficiency_level (0~5) 映射。
        job_skills_map: job_id -> {skill_id: required_level} 映射。
        relation_map: 技能关系映射，用于关系补偿计算。
        required_threshold: MUST 技能满足率阈值，低于此值扣分。

    Returns:
        list[dict]: 按综合分降序排列的匹配结果列表。
    """
    results: list[dict[str, Any]] = []
    user_ids = set(user_skills.keys())
    relation_map = relation_map or {}

    for job_id, job_skills in job_skills_map.items():
        job_ids = set(job_skills.keys())
        required_ids = {sid for sid, lvl in job_skills.items() if lvl == "MUST"}

        # 基础匹配
        base = match_user_to_job(user_skills, job_skills, required_ids)

        # 关系补偿
        relation_comp = 0.0
        if relation_map:
            relation_comp = calculate_relation_compensation(user_ids, job_ids, relation_map)

        # 最终综合分：基础分 * (1 + 关系补偿 * 0.2)
        composite = base["composite_score"]
        total_score = min(composite * (1.0 + relation_comp * 0.2), 1.0)

        # 检查 MUST 技能满足率
        if required_ids:
            required_met_count = len(required_ids & user_ids)
            required_rate = required_met_count / len(required_ids)
            if required_rate < required_threshold:
                total_score *= required_rate / required_threshold * 0.5

        # 构建匹配明细
        detail = {
            **base,
            "relation_compensation": round(relation_comp, 4),
            "total_score": round(total_score, 4),
        }

        results.append({
            "job_id": job_id,
            "score": round(total_score * 100, 2),
            "match_detail": detail,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def calculate_skill_gap(
    user_skill_ids: set[int],
    job_skills: dict[int, str],
    skill_names: dict[int, str],
) -> dict[str, Any]:
    """计算用户与岗位之间的技能差距分析。

    Args:
        user_skill_ids: 用户拥有的技能 ID 集合。
        job_skills: {skill_id: required_level} 映射。
        skill_names: {skill_id: skill_name} 映射。

    Returns:
        dict: 技能差距分析结果。
    """
    total_required = len(job_skills)
    if total_required == 0:
        return {
            "total_required": 0,
            "matching_skills": 0,
            "gap_skills": [],
            "match_rate": 1.0,
            "suggestions": ["无技能要求，可直接投递"],
        }

    matching = user_skill_ids & set(job_skills.keys())
    matching_count = len(matching)

    gap_skills = []
    for skill_id, req_level in sorted(job_skills.items(), key=lambda x: REQUIRED_LEVEL_WEIGHTS.get(x[1], 99)):
        if skill_id not in user_skill_ids:
            gap_skills.append({
                "skill_name": skill_names.get(skill_id, f"skill_{skill_id}"),
                "requirement_level": req_level,
            })

    match_rate = matching_count / total_required if total_required > 0 else 1.0

    suggestions = []
    if match_rate < 0.3:
        suggestions.append("技能匹配度过低，建议补充相关技能后再投递")
    elif match_rate < 0.6:
        suggestions.append("部分技能不足，可针对性地学习缺失技能")
    else:
        suggestions.append("技能匹配度良好，建议完善简历投递")

    must_gaps = [g for g in gap_skills if g["requirement_level"] == "MUST"]
    if must_gaps:
        must_names = [g["skill_name"] for g in must_gaps]
        suggestions.append(f"建议优先掌握以下必备技能：{'、'.join(must_names)}")

    return {
        "total_required": total_required,
        "matching_skills": matching_count,
        "gap_skills": gap_skills,
        "match_rate": round(match_rate, 4),
        "suggestions": suggestions,
    }
