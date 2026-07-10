# Day 11 — Admin 管理员模块

> **前置依赖**：day01 auth
> **前端对应**：AdminDashboard.vue / UserManage.vue / AuditManage.vue / SystemLogs.vue / AIModelConfig.vue
> **核心 ADR**：ADR-0010 + V4 Q19（企业审核）+ ADR-0003（技能字典审核）

---

## 目标

管理员后台：数据统计、用户管理、企业审核、技能字典审核、系统日志、AI 模型配置。

---

## 涉及数据表

- `user` / `company` — 用户与企业
- `skill` — 技能字典（CANDIDATE 审核/合并）
- `skill_synonym` — 同义词
- `operation_log` — 操作日志
- AI 模型配置（环境变量 / settings，不单独建表）

---

## API 清单

### 1. GET `/api/admin/stats`

- 需要 ADMIN 角色
- 管理员仪表盘统计数据
- 返回 `Result<{ user_count, job_count, company_count, today_applications, chart_data }>`

### 2. GET `/api/admin/users`

| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 用户名/邮箱搜索 |
| role | string | 角色筛选 |
| page/size | int | 分页 |

- 返回 `Result<PageData<UserVO>>`

### 3. PUT `/api/admin/user/{id}/ban`

| 参数 | 类型 | 说明 |
|------|------|------|
| action | string | ban / unban |

- status: NORMAL / BANNED
- 不能封禁 ADMIN
- 返回 `Result[null]`

### 4. GET `/api/admin/audit`

- 企业审核列表 + 技能字典审核列表（tab 切换）
- 企业：audit_status=[PENDING] 的 company 列表
- 技能：status=CANDIDATE 的 skill 列表
- 返回 `Result<{ companies: [...], skills: [...] }>`

### 5. PUT `/api/admin/audit/{id}`

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | company / skill |
| action | string | approve / reject |
| reason | string | 拒绝原因 |

- 企业：UNVERIFIED/PENDING → VERIFIED/REJECTED
- 技能：CANDIDATE → ACTIVE / MERGED
- 返回 `Result[null]`

### 6. GET `/api/admin/logs`

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | operation / login |
| keyword | string | 搜索 |
| page/size | int | 分页 |

- 返回 `Result<PageData<LogVO>>`

### 7. GET `/api/admin/ai-model`

- 需要 ADMIN 角色
- 返回当前 AI 模型配置（provider / api_key(脱敏) / base_url / model / temperature / max_tokens）
- 返回 `Result<AiModelConfigVO>`

### 8. PUT `/api/admin/ai-model`

- 更新 AI 模型配置
| 参数 | 类型 | 说明 |
|------|------|------|
| provider | string | 模型提供商 |
| api_key | string | API Key |
| base_url | string | endpoint |
| default_model | string | 默认模型 |
| temperature | float | 温度 |
| max_tokens | int | 最大 token |

- 写入环境变量 / settings 文件
- 返回 `Result[null]`

---

## 代码分层

| 层 | 文件 |
|----|------|
| 路由 | `api/v1/admin.py` |
| 服务 | `services/admin_service.py` |
| 仓储 | `repositories/user_repository.py` |
| 仓储 | `repositories/company_repository.py` |
| 仓储 | `repositories/skill_repository.py` |
| 仓储 | `repositories/log_repository.py` |

---

## 验收标准

- [ ] 仪表盘统计数据正确
- [ ] 用户搜索/封禁/解封
- [ ] 企业审核通过/拒绝
- [ ] 技能字典 CANDIDATE → ACTIVE
- [ ] 操作日志列表可查
- [ ] AI 模型配置可读可写
