# Day 13 — 图谱模块 + 管理日志

> **日期**：2026-07-18（周六）
> **阶段**：扩展功能
> **前置依赖**：Day 08（管理后台）+ Day 11（职业规划）

---

## 目标

完成能力图谱查询接口、系统操作日志查询、登录日志。

---

## 任务清单

### 1. 图谱模块接口（1.5h）

- [x] `AbilityGraph` 实体：id, entityType(USER/JOB), entityId, graphData(JSONB), updatedAt
- [x] `GET /api/graph/user/{userId}` — 个人能力图谱
  - 从 user_skill → skill → skill_relation 组装图数据
  - 返回 ECharts 格式 JSON（节点 + 边 + category 上色）
- `GET /api/graph/job/{jobId}` — 岗位能力图谱
  - 从 job_skill → skill → skill_relation 组装
- `GET /api/graph/gap/{userId}/{jobId}` — 缺口分析
  - 用户技能 vs 岗位要求对比
  - 缺口技能沿 PREREQUISITE 边反推前置链
- `POST /api/graph/reload` — 触发图谱重建（通知 AI 服务）

### 2. 操作日志查询接口（1h）

- `GET /api/admin/logs` — 操作日志列表（分页，支持模块/操作人/时间筛选）
- `GET /api/admin/logs/{id}` — 日志详情

### 3. 登录日志（0.5h）

- `LoginLog` 实体：id, userId, ip, userAgent, loginTime
- [x] 登录成功后自动写入 login_log
- `GET /api/admin/login-logs` — 登录日志列表（分页）

### 4. 登录日志自动记录（0.5h）

- 在 AuthService.login() 成功后，异步写入 login_log

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/graph/` | 图谱模块接口 |
| `GET /api/graph/user/{userId}` | 个人能力图谱 |
| `GET /api/graph/job/{jobId}` | 岗位能力图谱 |
| `GET /api/graph/gap/{userId}/{jobId}` | 缺口分析 |
| `GET /api/admin/logs` | 操作日志查询 |
| `GET /api/admin/login-logs` | 登录日志查询 |

---

## 验收标准

- [x] 个人图谱返回 ECharts JSON（节点 + 4 类边 + category 上色）
- [x] 岗位图谱正确返回
- [x] 缺口分析：用户技能 vs 岗位要求，缺失技能标红
- [x] 操作日志查询支持分页 + 筛选
- [x] 登录日志自动记录
