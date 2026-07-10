"""
图算法 — 基于 networkx 的技能图谱算法
"""

import networkx as nx


def find_shortest_path(graph: nx.DiGraph, source: int, target: int) -> list[int]:
    """
    查找两个技能之间的最短路径

    Args:
        graph: 技能图谱
        source: 起始节点 ID
        target: 目标节点 ID

    Returns:
        路径节点 ID 列表，无路径返回空列表
    """
    try:
        return nx.shortest_path(graph, source=source, target=target)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []


def get_related_skills(graph: nx.DiGraph, skill_id: int, max_depth: int = 2) -> list[int]:
    """
    获取指定技能的相关技能（BFS 遍历）

    Args:
        graph: 技能图谱
        skill_id: 技能节点 ID
        max_depth: 最大遍历深度

    Returns:
        相关技能 ID 列表
    """
    if skill_id not in graph:
        return []
    related = []
    visited = {skill_id}
    queue = [(skill_id, 0)]
    while queue:
        current, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        for neighbor in graph.successors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                related.append(neighbor)
                queue.append((neighbor, depth + 1))
    return related


def calculate_skill_similarity(graph: nx.DiGraph, skill_a: int, skill_b: int) -> float:
    """
    计算两个技能的相似度（基于共同邻居）

    Args:
        graph: 技能图谱
        skill_a: 技能 A 的 ID
        skill_b: 技能 B 的 ID

    Returns:
        相似度分数 0-1
    """
    if skill_a not in graph or skill_b not in graph:
        return 0.0
    neighbors_a = set(graph.successors(skill_a)) | set(graph.predecessors(skill_a))
    neighbors_b = set(graph.successors(skill_b)) | set(graph.predecessors(skill_b))
    if not neighbors_a or not neighbors_b:
        return 0.0
    intersection = neighbors_a & neighbors_b
    union = neighbors_a | neighbors_b
    return len(intersection) / len(union) if union else 0.0
