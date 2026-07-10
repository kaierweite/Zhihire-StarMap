"""图谱增值层：基于技能关系增强匹配分。

通过 skill_relation 表的关系边：
- SIMILAR：用户拥有相似技能时部分补偿
- PREREQUISITE：用户拥有前置技能时提示有基础
- COMPLEMENTARY：用户拥有互补技能加分

返回 graph_hints 文本列表。
"""
from typing import Any


def compute_graph_boost(
    user_skill_ids: set[int],
    job_skill_ids: set[int],
    relation_map: dict[int, dict[str, list[int]]],
    skill_names: dict[int, str],
) -> dict[str, Any]:
    """计算图谱增值评分和提示。

    Args:
        user_skill_ids: 用户技能 ID 集合。
        job_skill_ids: 岗位要求技能 ID 集合。
        relation_map: skill_id -> {relation_type: [related_skill_ids]} 关系映射。
        skill_names: skill_id -> skill_name 映射。

    Returns:
        dict: {"boost": float (0~1 加分系数), "hints": list[str]}
    """
    if not relation_map or not job_skill_ids:
        return {"boost": 0.0, "hints": []}

    missing = job_skill_ids - user_skill_ids
    if not missing:
        return {"boost": 0.0, "hints": ["技能全部命中"]}

    total_boost = 0.0
    hints: list[str] = []

    for missing_sid in missing:
        relations = relation_map.get(missing_sid, {})
        missing_name = skill_names.get(missing_sid, f"skill_{missing_sid}")

        # SIMILAR 补偿
        similar_ids = relations.get("SIMILAR", [])
        similar_overlap = set(similar_ids) & user_skill_ids
        if similar_overlap:
            similar_names = [skill_names.get(sid, f"skill_{sid}") for sid in similar_overlap]
            total_boost += 0.08 * len(similar_overlap)
            hints.append(
                f"您已掌握{'/'.join(similar_names)}（与{missing_name}相似），可快速上手"
            )

        # PREREQUISITE 补偿
        prereq_ids = relations.get("PREREQUISITE", [])
        prereq_overlap = set(prereq_ids) & user_skill_ids
        if prereq_overlap:
            prereq_names = [skill_names.get(sid, f"skill_{sid}") for sid in prereq_overlap]
            total_boost += 0.05 * len(prereq_overlap)
            hints.append(
                f"您已掌握{missing_name}的前置知识{'/'.join(prereq_names)}，学习门槛较低"
            )

        # COMPLEMENTARY 加分
        comp_ids = relations.get("COMPLEMENTARY", [])
        comp_overlap = set(comp_ids) & user_skill_ids
        if comp_overlap:
            total_boost += 0.03 * len(comp_overlap)

    total_boost = min(total_boost, 0.3)  # 封顶 30% boost

    return {
        "boost": round(total_boost, 4),
        "hints": hints,
    }
