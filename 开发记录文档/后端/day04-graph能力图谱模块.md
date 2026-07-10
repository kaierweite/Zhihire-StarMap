# Day 04 — Graph 能力图谱模块

> **前置依赖**：day03 简历解析（数据来源）+ day05 岗位（岗位图谱数据来源）
> **前端对应**：AbilityMap.vue
> **核心 ADR**：ADR-0005（图谱归口 AI 服务）

---

## 目标

基于解析后的结构化数据，为求职者构建个人能力图谱，为岗位构建岗位能力谱图，以 ECharts 关系图 JSON 返回前端渲染。

图谱本体是常驻内存的 networkx 图对象，`ability_graph` 表只存 ECharts payload 缓存。

---

## 涉及数据表

- `skill` — 技能字典（id, name, category, status）
- `skill_relation` — 技能关系（skill_id_a, skill_id_b, relation_type, weight）
- `role` — 职业角色
- `role_skill` — 角色技能关联（role_id, skill_id, requirement_level）
- `user_skill` — 用户技能
- `job_skill` — 岗位技能
- `ability_graph` — 图谱缓存（owner_type, owner_id, graph_json, updated_at）

---

## 图谱本体

- `skill_relation` 四类边：
  - PREREQUISITE — 前置依赖（学 Vue 前先学 HTML）
  - INCLUDES — 父子包含（前端开发 INCLUDES Vue 3）
  - SIMILAR — 相似技能（Vue 3 ~ React）
  - COMPLEMENTARY — 互补技能（Docker + K8s）
- `role_skill` 关联：MUST / NICE / BONUS 三级
- networkx 图对象常驻内存，发布时构建一次

---

## API 清单

### 1. GET `/api/graph/user`

- 需要 USER 角色
- 取当前用户 user_skill → 构建 ECharts 关系图 JSON
- 节点：技能名 + 类别颜色 + level
- 边：skill_relation 中的 PREREQUISITE / SIMILAR / INCLUDES
- 附带缺口视图 tab：对比目标 role 所需技能，标记已有/缺失
- 返回 `Result<{ nodes, edges, gap_skills }>`

### 2. GET `/api/graph/job/{job_id}`

- 取岗位 job_skill → 构建岗位能力谱图
- 节点：岗位技能 + category 着色
- 边：skill_relation 中的关系
- 返回 `Result<{ nodes, edges }>`

### 3. POST `/api/graph/reload`

- 需要 ADMIN 角色
- 手动触发图谱重建（技能字典变更后）
- 返回 `Result[null]`

---

## 代码分层

| 层 | 文件 | 职责 |
|----|------|------|
| 路由 | `api/v1/graph.py` | 三个端点 |
| 服务 | `services/graph_service.py` | 图谱构建编排 |
| 核心 | `core/graph/builder.py` | networkx 图构建 |
| 核心 | `core/graph/echarts_mapper.py` | networkx → ECharts JSON |
| 仓储 | `repositories/skill_repository.py` | |
| 仓储 | `repositories/skill_relation_repository.py` | |
| 仓储 | `repositories/ability_graph_repository.py` | |

---

## 验收标准

- [ ] 用户有技能 → GET 返回 nodes + edges + gap_skills
- [ ] 节点带 category 颜色
- [ ] edge 带 relation_type
- [ ] 缺口视图正确标记缺失技能
- [ ] 岗位图谱正确返回
