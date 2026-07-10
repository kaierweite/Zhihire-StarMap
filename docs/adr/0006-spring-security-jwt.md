# 鉴权采用 FastAPI Depends + JWT

鉴权统一用 python-jose + FastAPI Depends。`app/api/deps.py` 中 `get_current_user()` 解析 JWT token，从 payload 提取大写角色（ADMIN/USER/COMPANY），通过 `oauth2_scheme` + `HTTPBearer` 注入。路由用 `Depends(require_role("ADMIN"))` 做声明式角色校验。JWT claim 一律大写，与 ADR-0002 角色语义枚举口径一致。密码用 passlib bcrypt 加密。

不采用自写白名单中间件方案。赛题是求职者/企业/管理员三端隔离的高密度权限矩阵，演示中评委可见，`Depends` 声明式权限比手写白名单更稳、更可读。成本是正确处理大写角色，这条已由 ADR-0002 的大写语义枚举对齐。