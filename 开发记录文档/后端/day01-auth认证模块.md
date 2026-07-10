# Day 01 — Auth 认证模块

> **前置依赖**：day00 基础设施完成
> **前端对应**：LoginView.vue / RegisterView.vue

---

## 目标

实现用户注册、登录、获取当前用户信息，返回 JWT token + 角色。
前端已有 `api/auth.ts` 调用 `POST /auth/login` 和 `POST /auth/register`。

---

## 涉及数据表

- `user` — 用户主表（id, username, password_hash, role, email, phone, status, created_at, updated_at, deleted_at）
- `company` — 企业表（注册企业时关联创建）

---

## API 清单

### 1. POST `/api/auth/register`

注册求职者或企业。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码（明文传输，后端 bcrypt 加密） |
| role | string | 是 | USER / COMPANY |
| email | string | 否 | 邮箱 |
| phone | string | 否 | 手机号 |

- role=COMPANY 时额外接收企业名称等字段，创建 `company` 记录，`audit_status=UNVERIFIED`
- 密码 passlib bcrypt 加密后写入
- 返回 `Result[null]`

### 2. POST `/api/auth/login`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

- 校验用户名 + bcrypt 比对
- 生成 JWT，payload 含 `sub`(user_id), `role`, `exp`
- 返回 `Result<{ token, role, username }>`

### 3. GET `/api/auth/me`

- 需要 `Authorization: Bearer <token>`
- 返回当前用户完整信息 `Result<UserInfo>`

---

## 代码分层

| 层 | 文件 | 职责 |
|----|------|------|
| 路由 | `api/v1/auth.py` | 参数校验 + 调 service |
| 服务 | `services/auth_service.py` | 注册/登录逻辑 |
| 仓储 | `repositories/user_repository.py` | user 原子操作 |
| 仓储 | `repositories/company_repository.py` | company 原子操作 |
| 模型 | `models/entities/user.py` | User ORM |
| 模型 | `models/schemas/auth.py` | RegisterForm / LoginResult |

---

## 验收标准

- [ ] 求职者注册 → 登录 → 返回 token
- [ ] 企业注册 → 登录 → 返回 token（角色 COMPANY）
- [ ] 密码错误 → 返回 400
- [ ] 已注册用户名 → 返回 409
- [ ] token 可用于 `GET /api/auth/me`
