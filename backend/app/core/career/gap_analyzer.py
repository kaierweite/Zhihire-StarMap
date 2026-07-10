"""缺口分析核心算法。

基于用户已有技能与目标角色技能要求，计算技能缺口并按优先级排序。
"""
from app.models.schemas.graph import GapSkill


def analyze_skill_gap(
    user_skill_ids: set[int],
    role_skill_map: dict[int, str],
    skill_names: dict[int, str],
) -> list[GapSkill]:
    """分析用户技能与目标角色技能之间的缺口。

    返回按需求等级排序的缺口列表：MUST > NICE > BONUS。

    Args:
        user_skill_ids: 用户已掌握的技能主键集合。
        role_skill_map: 角色要求技能 {skill_id: requirement_level}。
        skill_names: 技能名映射 {skill_id: skill_name}。

    Returns:
        list[GapSkill]: 按优先级排序的缺口技能列表。
    """
    gaps: list[GapSkill] = []
    level_order = {"MUST": 0, "NICE": 1, "BONUS": 2}
    for skill_id, level in role_skill_map.items():
        if skill_id not in user_skill_ids:
            gaps.append(GapSkill(
                skill_name=skill_names.get(skill_id, f"skill_{skill_id}"),
                requirement_level=level,
            ))
    gaps.sort(key=lambda g: level_order.get(g.requirement_level, 99))
    return gaps


def compute_match_score(
    user_skill_ids: set[int],
    role_skill_ids: set[int],
    role_skill_map: dict[int, str],
) -> float:
    """计算用户技能与目标角色技能的匹配度（0~100）。

    MUST 技能权重 2，NICE 权重 1，BONUS 权重 0.5。
    匹配度 = 已有加权要求数 / 总加权要求数 * 100。

    Args:
        user_skill_ids: 用户已掌握的技能主键集合。
        role_skill_ids: 角色要求的全部技能主键集合。
        role_skill_map: 角色要求技能 {skill_id: requirement_level}。

    Returns:
        float: 匹配百分比（0~100），保留 1 位小数。
    """
    weight_map = {"MUST": 2.0, "NICE": 1.0, "BONUS": 0.5}
    total_weight = 0.0
    matched_weight = 0.0
    for skill_id in role_skill_ids:
        level = role_skill_map.get(skill_id, "NICE")
        w = weight_map.get(level, 1.0)
        total_weight += w
        if skill_id in user_skill_ids:
            matched_weight += w
    if total_weight == 0:
        return 0.0
    return round(matched_weight / total_weight * 100, 1)