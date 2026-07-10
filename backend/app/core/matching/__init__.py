"""岗位匹配算法核心模块（三层：召回→打分→图谱增值）。
"""
from app.core.matching.matcher import (
    composite_match_score, jaccard_similarity, match_user_to_job, weighted_skill_match,
)
from app.core.matching.scorer import (
    compute_breakdown, score_skill_dimension, score_edu_dimension,
    score_exp_dimension, score_city_dimension,
)
from app.core.matching.graph_boost import compute_graph_boost
from app.core.matching.rationale_builder import build_rationale
from app.core.matching.recall import recall_jobs_for_user, recall_candidates_for_job

__all__ = [
    "jaccard_similarity",
    "weighted_skill_match",
    "composite_match_score",
    "match_user_to_job",
    "compute_breakdown",
    "score_skill_dimension",
    "score_edu_dimension",
    "score_exp_dimension",
    "score_city_dimension",
    "compute_graph_boost",
    "build_rationale",
    "recall_jobs_for_user",
    "recall_candidates_for_job",
]
