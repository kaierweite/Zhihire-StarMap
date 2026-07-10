"""
图谱服务 — 图谱构建 / 重载 / 缺口分析
"""

import logging
from collections import defaultdict

from app.core.graph.skill_graph import skill_graph
from app.core.graph.algorithms import get_related_skills, find_shortest_path
from app.infrastructure.db_client import db_client

logger = logging.getLogger("zhihire.ai.graph")


async def reload_graph() -> dict:
    """从 DB 全量重建内存图"""
    skills = await db_client.fetch_skills()
    relations = await db_client.fetch_relations()
    skill_graph.rebuild(skills, relations)
    return {
        "node_count": skill_graph.get_node_count(),
        "edge_count": skill_graph.get_edge_count(),
    }


async def build_graph(skills: list[str], relations: list[dict]) -> dict:
    """
    构建图谱并返回 ECharts JSON
    如果传入了新数据则增量添加，否则返回当前图谱
    """
    if skills or relations:
        skill_dicts = [
            {"id": i, "name": s, "category": ""}
            for i, s in enumerate(skills)
        ]
        skill_graph.add_skills(skill_dicts)
        skill_graph.add_relations(relations)
    return skill_graph.to_echarts_json()


def get_community_categories() -> dict[str, list[int]]:
    """按 category 分簇"""
    g = skill_graph.graph
    clusters: dict[str, list[int]] = defaultdict(list)
    for node_id, data in g.nodes(data=True):
        cat = data.get("category", "未分类")
        clusters[cat].append(node_id)
    return dict(clusters)


def analyze_gap(user_skills: list[str], target_role: str) -> dict:
    """
    缺口分析：用户技能 vs 目标岗位所需技能
    沿 PREREQUISITE 边反推前置链

    Returns:
        {"gap_skills": [...], "prerequisite_chain": [...]}
    """
    g = skill_graph.graph
    # 找到目标岗位相关的技能节点
    user_set = set(s.lower() for s in user_skills)
    role_nodes = []
    for nid, data in g.nodes(data=True):
        name = data.get("name", "").lower()
        if target_role.lower() in name or name in user_set:
            role_nodes.append(nid)

    # 找目标岗位的 MUST 技能（沿 PREREQUISITE 边）
    must_skills = set()
    for nid, data in g.nodes(data=True):
        cat = data.get("category", "")
        if "必备" in cat or "必须" in cat:
            must_skills.add(nid)

    # 如果没找到 MUST 标记，用所有出度 > 0 的节点
    if not must_skills:
        must_skills = set(g.nodes())

    # 缺口 = MUST 技能 - 用户已有
    gap = []
    for nid in must_skills:
        name = g.nodes[nid].get("name", str(nid))
        if name.lower() not in user_set:
            gap.append(name)

    # 前置链：沿 PREREQUISITE 边追溯
    prereq_chain = []
    for nid in must_skills:
        for pred in g.predecessors(nid):
            edge_data = g.edges[pred, nid]
            if edge_data.get("relation_type") == "PREREQUISITE":
                prereq_name = g.nodes[pred].get("name", str(pred))
                if prereq_name.lower() not in user_set:
                    prereq_chain.append(prereq_name)

    return {
        "gap_skills": gap,
        "prerequisite_chain": list(set(prereq_chain)),
    }
