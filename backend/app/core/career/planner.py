"""学习路径规划核心算法。

基于技能 PREREQUISITE 依赖关系，对缺口技能进行拓扑排序，
生成有序学习路径，并附加图谱提示信息。
"""
import logging
import networkx as nx

logger = logging.getLogger(__name__)


def _build_prerequisite_digraph(
    all_skills: dict[int, str],
    relations: list[tuple[int, int, str]],
) -> nx.DiGraph:
    """从全局技能关系中提取 PREREQUISITE 边，构建有向图。

    skill_relation 表的 PREREQUISITE 边方向：skill_id_a → skill_id_b（a 是 b 的前置知识）。
    在有向图中，边方向为 a → b 表示"a 是 b 的前置"。

    Args:
        all_skills: 全部技能 {skill_id: skill_name}。
        relations: 技能关系 [(skill_id_a, skill_id_b, relation_type)]。

    Returns:
        nx.DiGraph: 仅含 PREREQUISITE 边的有向图。
    """
    DG = nx.DiGraph()
    for sid, name in all_skills.items():
        DG.add_node(sid, name=name)

    for a, b, rtype in relations:
        if rtype == "PREREQUISITE":
            DG.add_edge(a, b)

    return DG


def build_learning_path(
    gap_skill_ids: list[int],
    all_skills: dict[int, str],
    relations: list[tuple[int, int, str]],
) -> list[list[str]]:
    """为缺口技能构建有序学习路径（按 PREREQUISITE 拓扑排序）。

    Args:
        gap_skill_ids: 缺口技能主键列表。
        all_skills: 全部技能 {skill_id: skill_name}。
        relations: 技能关系 [(skill_id_a, skill_id_b, relation_type)]。

    Returns:
        list[list[str]]: 学习路径列表，每项为一个有序技能名称列表（前置在前）。
    """
    DG = _build_prerequisite_digraph(all_skills, relations)
    paths: list[list[str]] = []

    for skill_id in gap_skill_ids:
        ancestors: set[int] = set()
        stack = [skill_id]
        while stack:
            current = stack.pop()
            if current in ancestors:
                continue
            ancestors.add(current)
            for pred in DG.predecessors(current):
                if pred not in ancestors:
                    stack.append(pred)

        subgraph = DG.subgraph(ancestors)
        try:
            sorted_nodes = list(nx.topological_sort(subgraph))
            path_names = [
                all_skills.get(n, str(n))
                for n in sorted_nodes
                if n in ancestors
            ]
            target_name = all_skills.get(skill_id, str(skill_id))
            if target_name in path_names:
                path_names.remove(target_name)
                path_names.append(target_name)
            paths.append(path_names if path_names else [target_name])
        except nx.NetworkXUnfeasible:
            target_name = all_skills.get(skill_id, str(skill_id))
            paths.append([target_name])

    return paths


def generate_graph_hints(
    gap_skill_ids: list[int],
    all_skills: dict[int, str],
    relations: list[tuple[int, int, str]],
    user_skill_names: set[str],
) -> list[str]:
    """为缺口技能生成图谱提示信息。

    Args:
        gap_skill_ids: 缺口技能主键列表。
        all_skills: 全部技能 {skill_id: skill_name}。
        relations: 技能关系 [(skill_id_a, skill_id_b, relation_type)]。
        user_skill_names: 用户已掌握的技能名称集合。

    Returns:
        list[str]: 图谱提示列表。
    """
    hints: list[str] = []

    for gid in gap_skill_ids:
        gname = all_skills.get(gid, "")
        if not gname:
            continue

        for a, b, rtype in relations:
            related_sid = None
            if a == gid and rtype in ("SIMILAR", "COMPLEMENTARY"):
                related_sid = b
            elif b == gid and rtype in ("SIMILAR", "COMPLEMENTARY"):
                related_sid = a

            if related_sid is not None:
                rname = all_skills.get(related_sid, "")
                if rname and rname in user_skill_names:
                    if rtype == "SIMILAR":
                        hints.append(f"您已掌握{rname}（与{gname}相似），可快速上手")
                    elif rtype == "COMPLEMENTARY":
                        hints.append(f"您已掌握{rname}（与{gname}互补），结合学习效果更佳")

    return hints


def build_rationale(
    role_name: str,
    score: float,
    gap_count: int,
    llm_polish: str = "",
) -> str:
    """构建规划说明文本。

    Args:
        role_name: 目标角色名。
        score: 技能匹配度（0~100）。
        gap_count: 缺口技能数量。
        llm_polish: LLM 润色末句。

    Returns:
        str: 规划说明全文。
    """
    core = f"您与目标岗位「{role_name}」的技能匹配度为{score}%，主要缺口为{gap_count}项技能。以下学习路径按前置依赖排序，建议由浅入深系统学习。"
    if llm_polish:
        core += f" {llm_polish}"
    return core