"""\u804c\u4e1a\u89c4\u5212\u5f15\u64ce\u6838\u5fc3\u6a21\u5757\u3002
"""
from app.models.schemas.graph import GapSkill


def analyze_skill_gap(
    user_skill_ids: set[int],
    role_skill_map: dict[int, str],
    skill_names: dict[int, str],
) -> list[GapSkill]:
    """\u5206\u6790\u7528\u6237\u6280\u80fd\u4e0e\u76ee\u6807\u89d2\u8272\u6280\u80fd\u4e4b\u95f4\u7684\u7f3a\u53e3\u3002"""
    gaps: list[GapSkill] = []
    level_order = {"MUST": 0, "NICE": 1, "BONUS": 2}
    for skill_id, level in role_skill_map.items():
        if skill_id not in user_skill_ids:
            gaps.append(GapSkill(
                skill_name=skill_names.get(skill_id, f"skill_{skill_id}"),
                requirement_level=level,
            ))
    gaps.sort(key=lambda g: level_order.get(g.requirement_level, 99))
    return gaps


def recommend_career_paths(
    user_skill_ids: set[int],
    role_matches: list[tuple[int, str, float]],
    role_names: dict[int, str],
) -> list[dict]:
    """\u57fa\u4e8e\u6280\u80fd\u5339\u914d\u5ea6\u63a8\u8350\u804c\u4e1a\u8def\u5f84\u3002"""
    sorted_matches = sorted(role_matches, key=lambda x: x[2], reverse=True)
    results = []
    for role_id, _, score in sorted_matches[:5]:
        results.append({
            "role_id": role_id,
            "role_name": role_names.get(role_id, f"role_{role_id}"),
            "score": round(score, 4),
        })
    return results


def build_learning_path(gap_skill_ids: list[int], G: "nx.Graph", skill_names: dict[int, str]) -> list[list[str]]:
    """\u4e3a\u7f3a\u53e3\u6280\u80fd\u6784\u5efa\u5b66\u4e60\u8def\u5f84\u3002"""
    import networkx as nx
    paths = []
    for skill_id in gap_skill_ids:
        node = str(skill_id)
        if node not in G:
            continue
        try:
            predecessors = list(G.predecessors(node))
            prereq_names = [skill_names.get(int(p), p) for p in predecessors]
            path = prereq_names + [skill_names.get(skill_id, str(skill_id))]
            paths.append(path)
        except (nx.NetworkXError, nx.NodeNotFound):
            paths.append([skill_names.get(skill_id, str(skill_id))])
    return paths
