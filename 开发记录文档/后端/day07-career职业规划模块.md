# Day 07 — Career 职业规划模块

> **前置依赖**：day04 图谱 + day00 LLM 客户端
> **前端对应**：CareerPlan.vue
> **核心 ADR**：V4 Q6（图算法主力 + LLM 润色）

---

## 目标

基于用户能力图谱缺口分析，为目标职业角色生成有序学习路径。

规划主分由 networkx 图算法产出（拓扑排序/最短路径），LLM 仅做自然语言润色，不编分数和路径。

---

## 涉及数据表

- `career_plan` — 职业规划表（user_id, target_role_id, gap_skills JSONB, learning_path JSONB, graph_hints TEXT, rationale TEXT, source VARCHAR, created_at）
- `role` — 职业角色
- `role_skill` — 角色技能需求（MUST/NICE/BONUS）
- `skill_relation` — PREREQUISITE 边用于学习排序
- `user_skill` — 用户已有技能

---

## 算法

```
1. 用户选目标 role（或从最高推荐岗位反推 occupation_role）
2. 取 role_skill MUST 技能集 − user_skill 已有 = gap_skills
3. 对 gap_skills 沿 PREREQUISITE 边做拓扑排序 → learning_path
4. 附加 graph_hints：SIMILAR 技能关联、COMPLEMENTARY 补充建议
5. rationale 末句由 LLM 润色（输入是结构化结论，输出是自然话，不改变结果）
6. source 区分来源：INTERVIEW / PROACTIVE / RECOMMEND
```

---

## API 清单

### 1. POST `/api/career/plan/generate`

- 需要 USER 角色
| 参数 | 类型 | 说明 |
|------|------|------|
| target_role_id | int | 目标职业角色 |

- 运行上述算法
- 写入/更新 career_plan
- 返回 `Result<{ target_role, gap_skills[], learning_path[], graph_hints, rationale }>`

### 2. GET `/api/career/plan`

- 需要 USER 角色
- 获取当前用户已生成的职业规划
- 返回 `Result<CareerPlanVO>`

---

## 代码分层

| 层 | 文件 |
|----|------|
| 路由 | `api/v1/career.py` |
| 服务 | `services/career_service.py` |
| 核心 | `core/career/planner.py`（networkx 图算法） |
| 核心 | `core/career/gap_analyzer.py`（缺口分析） |
| 仓储 | `repositories/career_repository.py` |

---

## 验收标准

- [ ] 选择角色 → 返回缺口技能 + 有序学习路径
- [ ] 学习路径按 PREREQUISITE 拓扑排序
- [ ] 分数/路径不经大模型
- [ ] rationale 是模板拼接 + LLM 末句润色
