"""
推荐服务 — 匹配评分编排
"""

import logging

from app.core.recommender.matcher import calculate_match

logger = logging.getLogger("zhihire.ai.recommend")


async def match_candidates(user_skills: list[str], candidates: list[dict]) -> list[dict]:
    """
    批量匹配评分

    Args:
        user_skills: 用户技能列表
        candidates: 候选岗位列表

    Returns:
        按分数降序排列的匹配结果列表
    """
    results = []
    for candidate in candidates:
        result = calculate_match(user_skills, candidate)
        results.append(result)
    # 按分数降序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
