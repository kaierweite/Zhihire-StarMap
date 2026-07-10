"""维度打分层：可解释四维度子分计算。

| 维度 | 权重 | 算法 |
|------|------|------|
| 技能 | ~40% | importance 加权命中率；MUST/NICE/BONUS 分级权重 |
| 学历 | ~20% | 档差评分 |
| 经验 | ~20% | 年限比例 |
| 城市 | ~20% | 意向匹配 |

权重可通过 matching_weights 参数调整。
"""
from typing import Any

from app.models.entities.job import Job
from app.models.entities.user_profile import UserProfile

# 默认维度权重
DEFAULT_WEIGHTS: dict[str, float] = {
    "skill": 0.40,
    "edu": 0.20,
    "exp": 0.20,
    "city": 0.20,
}

# 技能要求级别权重
REQUIRED_LEVEL_WEIGHTS: dict[str, float] = {
    "MUST": 5.0,
    "NICE": 3.0,
    "BONUS": 1.0,
}

# 学历档位映射（从高到低）
EDU_LEVELS: dict[str, int] = {
    "博士": 6,
    "硕士": 5,
    "本科": 4,
    "大专": 3,
    "高中": 2,
    "初中": 1,
}


def score_skill_dimension(
    user_skills: dict[int, float],
    job_skills: dict[int, str],
    skill_importances: dict[int, float],
) -> dict[str, Any]:
    """技能维度评分。

    Args:
        user_skills: {skill_id: proficiency_level (0~5)}
        job_skills: {skill_id: required_level (MUST/NICE/BONUS)}
        skill_importances: {skill_id: importance (1~5)}

    Returns:
        dict: {"score": float (0~10), "hit": list[str], "miss": list[str], "detail": str}
    """
    if not job_skills:
        return {"score": 0, "hit": [], "miss": [], "detail": "无技能要求"}

    total_weight = 0.0
    earned_weight = 0.0
    hit: list[str] = []
    miss: list[str] = []

    for skill_id, req_level in job_skills.items():
        imp = skill_importances.get(skill_id, 3.0)
        level_weight = REQUIRED_LEVEL_WEIGHTS.get(req_level, 1.0)
        w = imp * level_weight
        total_weight += w

        user_prof = user_skills.get(skill_id, 0.0)
        if user_prof > 0:
            # 熟练度比例折算
            earned_weight += w * min(user_prof / 5.0, 1.0)
            hit.append(str(skill_id))
        else:
            miss.append(str(skill_id))

    if total_weight == 0:
        return {"score": 0, "hit": [], "miss": [], "detail": "无技能要求"}

    raw_score = (earned_weight / total_weight) * 10.0
    must_total = sum(1 for lvl in job_skills.values() if lvl == "MUST")
    must_hit = sum(
        1 for sid, lvl in job_skills.items()
        if lvl == "MUST" and user_skills.get(sid, 0) > 0
    ) if must_total > 0 else 0

    detail_parts = []
    if must_total > 0:
        detail_parts.append(f"必备{must_hit}/{must_total}")
    detail_parts.append(f"技能分{raw_score:.1f}")

    return {
        "score": round(raw_score, 2),
        "hit": hit,
        "miss": miss,
        "detail": "、".join(detail_parts),
    }


def score_edu_dimension(
    user_edu: str | None,
    job_edu: str | None,
) -> dict[str, Any]:
    """学历维度评分。

    Args:
        user_edu: 用户最高学历。
        job_edu: 岗位要求学历。

    Returns:
        dict: {"score": float (0~10), "detail": str}
    """
    if not job_edu:
        return {"score": 10, "detail": "无学历要求"}

    user_level = EDU_LEVELS.get(user_edu, 0) if user_edu else 0
    job_level = EDU_LEVELS.get(job_edu, 0)

    if user_level == 0:
        return {"score": 0, "detail": f"未提供学历信息，岗位要求{job_edu}"}

    diff = user_level - job_level
    if diff >= 0:
        # 达标或超标
        bonus = min(diff, 2) * 1.0  # 每超一档加 1 分
        score = min(10.0 + bonus, 12.0)
        label = "达标" if diff == 0 else f"超标+{diff}档"
        return {"score": round(score, 2), "detail": f"{user_edu}，{label}"}
    else:
        # 低档打折
        discount = 1.0 + abs(diff) * 0.3  # 每低一档打 7 折
        score = max(10.0 / discount, 2.0)
        return {"score": round(score, 2), "detail": f"{user_edu}，低{abs(diff)}档"}


def score_exp_dimension(
    user_exp_years: float | None,
    job_exp_min: int | None,
) -> dict[str, Any]:
    """经验维度评分。

    Args:
        user_exp_years: 用户工作年限。
        job_exp_min: 岗位要求最低年限。

    Returns:
        dict: {"score": float (0~10), "detail": str}
    """
    if not job_exp_min or job_exp_min <= 0:
        return {"score": 10, "detail": "无经验要求"}

    if not user_exp_years or user_exp_years <= 0:
        return {"score": 0, "detail": f"无工作经验，岗位要求{job_exp_min}年"}

    ratio = user_exp_years / job_exp_min
    score = min(ratio * 10.0, 10.0)
    status = "达标" if ratio >= 1.0 else f"不足({ratio:.0%})"
    return {
        "score": round(score, 2),
        "detail": f"{user_exp_years}年，{status}",
    }


def score_city_dimension(
    user_city: str | None,
    job_city: str | None,
) -> dict[str, Any]:
    """城市维度评分。

    Args:
        user_city: 用户所在/意向城市。
        job_city: 岗位所在城市。

    Returns:
        dict: {"score": float (0~10), "detail": str}
    """
    if not job_city:
        return {"score": 10, "detail": "无地点要求"}

    if not user_city:
        return {"score": 5, "detail": "未提供意向城市"}

    if user_city == job_city:
        return {"score": 10, "detail": "居住与岗位城市一致"}
    else:
        # 非同城，部分降分
        return {"score": 5, "detail": f"居住{user_city}，岗位在{job_city}"}


def compute_breakdown(
    user_skills: dict[int, float],
    job_skills: dict[int, str],
    skill_importances: dict[int, float],
    user_edu: str | None,
    job_edu: str | None,
    user_exp_years: float | None,
    job_exp_min: int | None,
    user_city: str | None,
    job_city: str | None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """计算完整的四维度分解 + 总分。

    Returns:
        dict: {"score": float, "breakdown": {...}, "rationale": str}
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}

    skill_result = score_skill_dimension(user_skills, job_skills, skill_importances)
    edu_result = score_edu_dimension(user_edu, job_edu)
    exp_result = score_exp_dimension(user_exp_years, job_exp_min)
    city_result = score_city_dimension(user_city, job_city)

    total_score = (
        skill_result["score"] * w["skill"]
        + edu_result["score"] * w["edu"]
        + exp_result["score"] * w["exp"]
        + city_result["score"] * w["city"]
    )

    breakdown = {
        "skill": skill_result,
        "edu": edu_result,
        "exp": exp_result,
        "city": city_result,
    }

    return {
        "score": round(total_score, 2),
        "breakdown": breakdown,
    }
