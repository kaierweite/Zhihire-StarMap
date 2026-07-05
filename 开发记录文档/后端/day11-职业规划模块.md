# Day 11 — 职业规划模块

> **日期**：2026-07-16（周四）
> **阶段**：核心业务（四）
> **前置依赖**：Day 09（匹配推荐）+ Day 05（技能字典）

---

## 目标

完成职业规划接口：调 AI 图算法 + LLM 润色 + 结构化存储。

---

## 任务清单

### 1. CareerPlan 实体（0.5h）

- [x] `CareerPlan` 实体：id, userId, targetRoleId, gapSkills(JSONB), learningPath(JSONB), graphHints(JSONB), rationale, source(INTERVIEW/PROACTIVE/RECOMMEND), createdAt

### 2. 职业规划接口（2h）

- [x] `GET /api/career/plan` — 获取当前用户的职业规划
- `POST /api/career/plan` — 生成/更新职业规划
  - 入参：targetRoleId（可选，不传则从最高推荐岗位反推）
  - [x] 调 AI 服务 `POST /ai/career/analyze`
  - AI 返回：gap_skills[], learning_path[], graph_hints, rationale + LLM 润色句
  - [x] 写入 career_plan 表
- `GET /api/career/roles` — 获取职业角色列表（occupation_role 表）

### 3. 职业规划历史（0.5h）

- `GET /api/career/plan/history` — 历史规划列表

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/career/entity/CareerPlan.java` | 职业规划实体 |
| `module/career/controller/CareerController.java` | 职业规划接口 |
| `POST /api/career/plan` | 生成职业规划 |
| `GET /api/career/roles` | 职业角色列表 |

---

## 验收标准

- [x] 职业角色列表正确返回 8~12 个角色
- [x] 规划生成：图算法缺口集 + 拓扑排序学习路径
- [x] LLM 仅润色，不改结构化结果
- [x] source 字段正确标记来源
