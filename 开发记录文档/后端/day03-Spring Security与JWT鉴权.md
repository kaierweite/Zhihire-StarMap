# Day 03 — Spring Security + JWT 鉴权

> **日期**：2026-07-08（周三）
> **阶段**：基础搭建
> **前置依赖**：Day 01（项目骨架）+ Day 02（user 表）

---

## 目标

完成三角色（ADMIN/USER/COMPANY）注册登录、JWT 签发与校验、Spring Security 配置。

---

## 任务清单

### 1. User 实体与 Mapper（1h）

- [x] `module.user.entity.User`：id, username, password, role(VARCHAR), status(VARCHAR), createdAt, updatedAt, deletedAt
- [x] `module.user.mapper.UserMapper` extends BaseMapper<User>
- `application.yml` 配置 MyBatis-Plus 自动填充

### 2. Auth 模块 — 注册接口（1.5h）

- `module.auth.dto.RegisterRequest`：username, password, role(USER/COMPANY)
- [x] `module.auth.service.AuthService.register()`：
  - [x] 校验用户名唯一
  - BCrypt 加密密码
  - 写入 user 表
  - 若 role=COMPANY，同步创建 company 记录（audit_status=UNVERIFIED）
- `module.auth.controller.AuthController`：
  - [x] `POST /api/auth/register` → `Result<Void>`

### 3. Auth 模块 — 登录接口（1.5h）

- `module.auth.dto.LoginRequest`：username, password
- [x] `module.auth.dto.LoginResponse`：token, role, userId, nickname
- [x] `module.auth.service.AuthService.login()`：
  - [x] 校验用户名存在
  - BCrypt 校验密码
  - 签发 JWT（claim: sub=userId, role=大写角色, exp=24h）
- `module.auth.controller.AuthController`：
  - [x] `POST /api/auth/login` → `Result<LoginResponse>`

### 4. JWT 过滤器（1.5h）

- `config.JwtAuthenticationFilter` extends OncePerRequestFilter：
  - [x] 从 Authorization header 提取 Bearer token
  - 解析 JWT claim，提取 userId 和 role
  - 将大写角色映射为 GrantedAuthority（ROLE_ADMIN/ROLE_USER/ROLE_COMPANY）
  - 设置 SecurityContext
- `config.SecurityConfig`：
  - [x] 禁用 CSRF
  - 配置 URL 授权规则：
    - [x] `/api/auth/**` permitAll
    - `/api/ping` permitAll
    - `/api/admin/**` hasRole("ADMIN")
    - 其他 authenticated
  - 添加 JwtAuthenticationFilter 在 UsernamePasswordAuthenticationFilter 之前
  - 配置 CORS

### 5. 测试验证（0.5h）

- 注册求职者：`POST /api/auth/register {username:"test", password:"12345678", role:"USER"}`
- [x] 注册企业：`POST /api/auth/register {username:"company1", password:"12345678", role:"COMPANY"}`
- [x] 登录获取 token：`POST /api/auth/login {username:"test", password:"12345678"}`
- 用 token 访问受保护接口
- 无 token 访问返回 401
- 用 USER 角色 token 访问 `/api/admin/**` 返回 403

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/user/entity/User.java` | 用户实体 |
| `module/user/mapper/UserMapper.java` | 用户 Mapper |
| `module/auth/` | 注册/登录 Controller + Service + DTO |
| `config/SecurityConfig.java` | Spring Security 配置 |
| `config/JwtAuthenticationFilter.java` | JWT 过滤器 |
| `POST /api/auth/register` | 注册接口 |
| `POST /api/auth/login` | 登录接口（返回 JWT） |

---

## 验收标准

- [x] 三角色注册成功，密码 BCrypt 加密存储
- [x] 登录返回 JWT token，claim 含大写角色
- [x] JWT 过滤器正确解析 token 并设置 SecurityContext
- [x] hasRole("ADMIN") 声明式权限生效
- [x] 无 token 返回 401，权限不足返回 403

