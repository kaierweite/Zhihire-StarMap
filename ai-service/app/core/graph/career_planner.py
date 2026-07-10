"""
职业规划器 — 缺口计算 + 拓扑排序学习路径 + LLM 润色
"""

import logging

import networkx as nx

from app.core.graph.skill_graph import skill_graph
from app.infrastructure.llm_client import llm_client

logger = logging.getLogger("zhihire.ai.career")


def compute_gap(user_skills: list[str], target_role: str) -> list[str]:
    """
    计算缺口集 = 目标岗位 MUST 技能 - 用户已有技能

    Returns:
        缺口技能名称列表
    """
    g = skill_graph.graph
    user_set = set(s.lower() for s in user_skills)
    # 找目标岗位节点
    role_nodes = []
    for nid, data in g.nodes(data=True):
        name = data.get("name", "").lower()
        cat = data.get("category", "").lower()
        if target_role.lower() in name or target_role.lower() in cat:
            role_nodes.append(nid)
    # 沿 PREREQUISITE/INCLUDES 边收集 MUST 技能
    must_skills: set[int] = set()
    for rn in role_nodes:
        for pred in g.predecessors(rn):
            edge = g.edges[pred, rn]
            if edge.get("relation_type") in ("PREREQUISITE", "INCLUDES"):
                must_skills.add(pred)
        must_skills.add(rn)
    # 如果没找到关系，用所有节点
    if not must_skills:
        must_skills = set(g.nodes())
    gap = []
    for nid in must_skills:
        name = g.nodes[nid].get("name", str(nid))
        if name.lower() not in user_set:
            gap.append(name)
    return gap


def compute_learning_path(gap_skills: list[str]) -> list[dict]:
    """
    沿 PREREQUISITE 边拓扑排序 → 有序学习路径

    Returns:
        [{"skill": "...", "priority": "high/medium/low", "resources": []}]
    """
    g = skill_graph.graph
    # 构建缺口子图
    gap_lower = {s.lower(): s for s in gap_skills}
    subgraph_nodes = []
    for nid, data in g.nodes(data=True):
        if data.get("name", "").lower() in gap_lower:
            subgraph_nodes.append(nid)
    if not subgraph_nodes:
        return [{"skill": s, "priority": "medium", "resources": []} for s in gap_skills]
    sub = g.subgraph(subgraph_nodes)
    # 只保留 PREREQUISITE 边做拓扑排序
    prereq_graph = nx.DiGraph()
    for nid in sub.nodes():
        prereq_graph.add_node(nid)
    for src, tgt, data in sub.edges(data=True):
        if data.get("relation_type") == "PREREQUISITE":
            prereq_graph.add_edge(src, tgt)
    # 拓扑排序
    try:
        ordered = list(nx.topological_sort(prereq_graph))
    except nx.NetworkXUnfeasible:
        # 有环则按原始顺序
        ordered = subgraph_nodes
    path = []
    for i, nid in enumerate(ordered):
        name = g.nodes[nid].get("name", str(nid))
        priority = "high" if i < len(ordered) // 3 else ("medium" if i < 2 * len(ordered) // 3 else "low")
        path.append({"skill": name, "priority": priority, "resources": []})
    return path


async def polish_with_llm(
    gap_skills: list[str],
    learning_path: list[dict],
    target_role: str,
) -> str:
    """LLM 仅润色文本，不改结构化结果"""
    path_text = " → ".join(item["skill"] for item in learning_path)
    prompt = (
        f"用户想成为「{target_role}」，目前缺少以下技能：{', '.join(gap_skills)}。\n"
        f"建议学习顺序：{path_text}\n\n"
        "请用一段通顺的中文给出职业规划建议，100字以内。"
    )
    try:
        return await llm_client.chat(prompt, temperature=0.7)
    except Exception as e:
        logger.warning(f"LLM 润色失败: {e}")
        return f"建议按顺序学习：{path_text}"
