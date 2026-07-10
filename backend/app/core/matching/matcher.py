"""\u5c97\u4f4d\u5339\u914d\u7b97\u6cd5\u6838\u5fc3\u6a21\u5757\u3002
"""


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """\u8ba1\u7b97\u4e24\u4e2a\u96c6\u5408\u7684 Jaccard \u76f8\u4f3c\u5ea6\u3002"""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    if not union:
        return 0.0
    return len(intersection) / len(union)


def weighted_skill_match(
    user_skills: dict[int, float],
    job_skills: dict[int, str],
    skill_weights: dict[str, float] | None = None,
) -> float:
    """\u8ba1\u7b97\u52a0\u6743\u6280\u80fd\u5339\u914d\u5ea6\u3002"""
    if not job_skills:
        return 0.0
    weights = skill_weights or {"MUST": 1.0, "NICE": 0.6, "BONUS": 0.3}
    total_score = 0.0
    max_possible = 0.0
    for skill_id, req_level in job_skills.items():
        weight = weights.get(req_level, 0.3)
        max_possible += weight
        user_level = user_skills.get(skill_id, 0.0)
        if user_level > 0:
            normalized = min(user_level / 5.0, 1.0)
            total_score += weight * normalized
    if max_possible == 0.0:
        return 0.0
    return total_score / max_possible


def composite_match_score(jaccard: float, weighted_score: float, jaccard_weight: float = 0.3, weighted_weight: float = 0.7) -> float:
    """\u7efc\u5408\u5339\u914d\u8bc4\u5206\u3002"""
    return jaccard * jaccard_weight + weighted_score * weighted_weight


def match_user_to_job(user_skills: dict[int, float], job_skills: dict[int, str], job_required_ids: set[int] | None = None) -> dict:
    """\u5b8c\u6574\u5339\u914d\u7528\u6237\u4e0e\u5c97\u4f4d\u3002"""
    user_ids = set(user_skills.keys())
    job_ids = set(job_skills.keys())
    required_ids = job_required_ids or {sid for sid, lvl in job_skills.items() if lvl == "MUST"}
    matched = list(user_ids & job_ids)
    missing = list(job_ids - user_ids)
    required_met = required_ids.issubset(user_ids)
    jaccard = jaccard_similarity(user_ids, job_ids)
    weighted = weighted_skill_match(user_skills, job_skills)
    composite = composite_match_score(jaccard, weighted)
    return {
        "jaccard": round(jaccard, 4),
        "weighted_score": round(weighted, 4),
        "composite_score": round(composite, 4),
        "matched_skills": matched,
        "missing_skills": missing,
        "required_met": required_met,
    }
