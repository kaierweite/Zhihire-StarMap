"""职业规划核心模块。

包含缺口分析（gap_analyzer）与学习路径规划（planner）两个子模块。
遗留 career_engine 保持向后兼容。
"""
from app.core.career.career_engine import (
    analyze_skill_gap as legacy_analyze_skill_gap,
    build_learning_path as legacy_build_learning_path,
    recommend_career_paths,
)
from app.core.career.gap_analyzer import analyze_skill_gap, compute_match_score
from app.core.career.planner import (
    build_learning_path,
    build_rationale,
    generate_graph_hints,
)

__all__ = [
    "analyze_skill_gap",
    "compute_match_score",
    "build_learning_path",
    "generate_graph_hints",
    "build_rationale",
    "recommend_career_paths",
    "legacy_analyze_skill_gap",
    "legacy_build_learning_path",
]