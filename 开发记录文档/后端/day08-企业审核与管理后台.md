# Day 08 — 企业审核 + 管理后台基础

> **日期**：2026-07-13（周一）
> **阶段**：核心业务（二）
> **前置依赖**：Day 03（鉴权）+ Day 05（技能归一）

---

## 目标

完成企业资质审核流程、管理后台用户管理、岗位下架/用户封禁。

---

## 任务清单

### 1. 企业审核接口（1.5h）

- [x] `GET /api/admin/company/list` — 企业列表（按 audit_status 筛选，分页）
- `PUT /api/admin/company/{id}/audit` — 审核企业
  - audit_status: UNVERIFIED → PENDING → VERIFIED / REJECTED
  - REJECTED 时必须传 auditReason
- 审核通过后：企业岗位 status 从 DRAFT → OPEN

### 2. 用户管理接口（1h）

- [x] `GET /api/admin/user/list` — 用户列表（支持 role/status 筛选，分页）
- `PUT /api/admin/user/{id}/ban` — 封禁用户（status=BANNED）
- `PUT /api/admin/user/{id}/unban` — 解封用户（status=NORMAL）

### 3. 岗位下架接口（0.5h）

- `PUT /api/admin/job/{id}/close` — 强制下架岗位（status=CLOSED）

### 4. 统计接口（1h）

- `StatService`：SQL 实时聚合 + Caffeine 短缓存（5 分钟）
- [x] `GET /api/admin/stat` → `{userCount, companyCount, jobCount, matchCount, parseCount}`
- 用 `COUNT` 统计各表记录数

### 5. 操作日志 AOP（1h）

- `@OperationLog("模块/动作")` 自定义注解
- `OperationLogAspect` AOP 切面：
  - [x] 拦截带 @OperationLog 的方法
  - 记录：操作人 userId、模块、动作、参数、结果、时间
  - [x] 写入 operation_log 表
- 覆盖：登录、岗位发布、字典审核、推荐触发

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/admin/controller/AdminCompanyController.java` | 企业审核 |
| `module/admin/controller/AdminUserController.java` | 用户管理 |
| `module/admin/controller/AdminJobController.java` | 岗位下架 |
| `module/admin/service/StatService.java` | 统计聚合 |
| `module/system/annotation/OperationLog.java` | 操作日志注解 |
| `module/system/aspect/OperationLogAspect.java` | AOP 切面 |
| `GET /api/admin/stat` | 统计数据接口 |

---

## 验收标准

- [x] 企业审核流程：UNVERIFIED → PENDING → VERIFIED/REJECTED
- [x] 审核通过后企业岗位自动 OPEN
- [x] 用户封禁/解封生效
- [x] 统计接口返回五项计数
- [x] @OperationLog AOP 自动记录操作日志
