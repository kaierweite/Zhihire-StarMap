"""可解释拼接层：按 breakdown 模板拼接 rationale。

不允许大模型逐条生成分数解释，由后端按规则模板拼装。
"""
from typing import Any


def build_rationale(breakdown: dict[str, Any], graph_hints: list[str]) -> str:
    """按 breakdown 维度结果拼装可解释文本。

    Args:
        breakdown: {"skill": {...}, "edu": {...}, "exp": {...}, "city": {...}}
        graph_hints: 图谱增值提示列表。

    Returns:
        str: 拼装好的 rationale 文本。
    """
    parts: list[str] = []

    # 技能维度
    skill = breakdown.get("skill", {})
    skill_detail = skill.get("detail", "")
    miss = skill.get("miss", [])
    if skill_detail:
        parts.append(skill_detail)
    if miss:
        parts.append(f"缺{len(miss)}项技能")

    # 学历维度
    edu = breakdown.get("edu", {})
    edu_detail = edu.get("detail", "")
    if edu_detail:
        parts.append(edu_detail)

    # 经验维度
    exp = breakdown.get("exp", {})
    exp_detail = exp.get("detail", "")
    if exp_detail:
        parts.append(exp_detail)

    # 城市维度
    city = breakdown.get("city", {})
    city_detail = city.get("detail", "")
    if city_detail:
        parts.append(city_detail)

    # 建议
    if miss:
        parts.append(f"补{min(len(miss), 3)}个缺口技能即可提升匹配度")

    rationale = "、".join(parts)

    # graph_hints 追加为建议
    if graph_hints:
        hint_text = "；".join(graph_hints[:3])
        rationale += f"。{hint_text}"

    return rationale
