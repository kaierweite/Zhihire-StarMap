"""
匹配评分器 — 计算用户技能与岗位的匹配度
"""


def calculate_match_score(
    user_skills: list[str],
    job_skills: list[str],
) -> tuple[float, dict]:
    """
    计算技能匹配分数

    Args:
        user_skills: 用户技能列表
        job_skills: 岗位要求技能列表

    Returns:
        (综合分数 0-100, 分项得分 breakdown)
    """
    if not job_skills:
        return 100.0, {"coverage": 1.0, "matched": [], "missing": []}

    user_set = set(s.lower().strip() for s in user_skills)
    job_set = set(s.lower().strip() for s in job_skills)

    matched = user_set & job_set
    missing = job_set - user_set

    coverage = len(matched) / len(job_set) if job_set else 0.0
    score = round(coverage * 100, 2)

    breakdown = {
        "coverage": round(coverage, 4),
        "matched_count": len(matched),
        "missing_count": len(missing),
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
    }
    return score, breakdown
