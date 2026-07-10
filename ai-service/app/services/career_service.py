"""
职业规划服务 — 编排缺口计算 + 学习路径 + LLM 润色
"""

import logging

from app.core.graph.career_planner import compute_gap, compute_learning_path, polish_with_llm

logger = logging.getLogger("zhihire.ai.career")


async def analyze_career(user_skills: list[str], target_role: str) -> dict:
    """
    职业规划分析

    Returns:
        {gap_skills, learning_path, rationale}
    """
    gap = compute_gap(user_skills, target_role)
    path = compute_learning_path(gap)
    rationale = await polish_with_llm(gap, path, target_role)
    return {
        "gap_skills": gap,
        "learning_path": path,
        "rationale": rationale,
    }
