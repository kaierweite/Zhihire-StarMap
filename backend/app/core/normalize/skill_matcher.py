"""技能归一核心算法（无外部依赖）。

将用户输入的自由形式技能名归一到标准 `skill_id`：
1. 大小写/空白/分隔符归一化后，按 skill.name 精确匹配；
2. 命中则取该 skill_id；
3. 未命中则查 skill_synonym 表，映射到标准 skill_id；
4. 仍未命中则标记为待人工审核的候选技能（status=CANDIDATE），由仓储层创建。

本模块仅做归一所需的数据准备与决策，真正的数据库读写由服务层调用仓储完成。
这里对外暴露的依据：给一批"已查到的技能名映射""已查到的同义词映射"，
返回每个输入应使用的 skill_id（None 表示需新建候选技能）。
"""


def normalize_skill_name(raw: str) -> str:
    """对技能名做基础归一化，便于精确匹配。

    统一为去除首尾空白、内部空白压缩、保留大小写（因为 skill 名本身有大小写语义，
    如 "Vue.js" 与 "vue.js"，故此处不做大小写折叠，仅在匹配时大小写不敏感地兜底）。

    Args:
        raw: 用户输入的原始技能名。

    Returns:
        str: 归一化后的技能名（可能仍含大小写，用于精确匹配库中标准名）。
    """
    # 去首尾空白并对内部连续空白压缩为单空格
    return " ".join(raw.strip().split())


def match_skills(
    raw_names: list[str],
    exact_map: dict[str, "object"],
    synonym_map: dict[str, int],
) -> dict[str, int | None]:
    """根据已查到的精确匹配与同义词映射，为每个输入技能名求归一结果。

    匹配优先级：
      a. 归一化后名称在 exact_map（按 skill.name 精确匹配）中 -> 取其 id；
      b. 归一化后名称在 synonym_map（skill_synonym 表）中 -> 取映射的 skill_id；
      c. 原始输入（归一化后）在 exact_map 中以大小写不敏感方式命中 -> 取其 id；
      d. 以上均未命中 -> 标记 None，表示需新建候选技能。

    Args:
        raw_names: 用户输入的原始技能名列表。
        exact_map: 已查到的 skill.name -> Skill 实例 映射。
        synonym_map: 已查到的 synonym -> skill_id 映射。

    Returns:
        dict[str, int | None]: 归一化后技能名 -> 归一 skill_id（None 表示需新建候选）。
    """
    # 构造大小写不敏感的精确匹配兜底表：lower(name) -> skill_id
    lower_exact: dict[str, int] = {}
    for name, skill in exact_map.items():
        lower_exact[name.lower()] = getattr(skill, "id", None)

    result: dict[str, int | None] = {}
    for raw in raw_names:
        norm = normalize_skill_name(raw)
        if not norm:
            continue
        # 1) 精确匹配（区分大小写）
        skill = exact_map.get(norm)
        if skill is not None and getattr(skill, "id", None) is not None:
            result[norm] = skill.id
            continue
        # 2) 同义词映射
        syn_id = synonym_map.get(norm)
        if syn_id is not None:
            result[norm] = syn_id
            continue
        # 3) 大小写不敏感的精确匹配兜底
        low_id = lower_exact.get(norm.lower())
        if low_id is not None:
            result[norm] = low_id
            continue
        # 4) 未命中，需新建候选技能
        result[norm] = None
    return result
