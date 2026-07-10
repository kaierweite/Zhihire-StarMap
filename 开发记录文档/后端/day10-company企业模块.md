# Day 10 — Company 企业模块

> **前置依赖**：day01 auth
> **前端对应**：CompanyDashboard.vue / CompanyLayout.vue
> **核心 ADR**：V4 Q19（企业审核）

---

## 目标

企业信息读取与编辑、企业首页统计数据。

---

## 涉及数据表

- `company` — 企业表（user_id, name, industry, size, description, logo, audit_status, audit_reason, created_at）
- `job` — 岗位表（用于统计）
- `recommend_record` — 推荐记录（用于统计投递数）

---

## API 清单

### 1. GET `/api/company/info`

- 需要 COMPANY 角色
- 返回企业信息 + 审核状态
- 返回 `Result<CompanyVO>`

### 2. PUT `/api/company/info`

- 编辑企业信息（名称/行业/规模/简介/logo）
- 编辑后 audit_status 重置为 PENDING（需重新审核）
- 返回 `Result<CompanyVO>`

### 3. GET `/api/company/dashboard`

- 需要 COMPANY 角色
- 企业首页统计数据
- 返回 `Result<{ stats: { total_jobs, active_jobs, received_resumes, pending_audit }, recent_jobs, recent_resumes }>`

---

## 代码分层

| 层 | 文件 |
|----|------|
| 路由 | `api/v1/company.py` |
| 服务 | `services/company_service.py` |
| 仓储 | `repositories/company_repository.py` |

---

## 验收标准

- [ ] 企业可查看自己信息 + 审核状态
- [ ] 编辑信息 → audit_status 重置 PENDING
- [ ] 首页统计正确返回
