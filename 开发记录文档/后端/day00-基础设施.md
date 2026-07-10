# Day 00 — 基础设施搭建

> **前置依赖**：Python 3.10+、KingbaseES 已启动
> **阶段**：骨架先行，所有业务模块的前置

---

## 目标

完成 FastAPI 工程骨架、数据库连接、JWT 鉴权依赖、统一响应封装、全局异常处理。
前端 `GET /api/ping` 能返回 200。

---

## 任务清单

- [ ] 安装核心依赖
  - fastapi, uvicorn[standard], sqlalchemy[asyncio], asyncpg
  - alembic, python-jose[cryptography], passlib[bcrypt]
  - aiocache, pdfplumber, python-docx, networkx
  - httpx（调 DeepSeek API）, pydantic-settings

- [ ] `app/main.py` — FastAPI 入口，挂载路由 + CORS + 异常处理器
- [ ] `app/config/settings.py` — Pydantic Settings，读取环境变量
  - DB 连接串 / DeepSeek API Key / JWT Secret / 文件存储路径
- [ ] `app/db/session.py` — async engine + AsyncSessionLocal + get_db 依赖
- [ ] `app/models/schemas/result.py` — `Result[T]` 统一响应模型
- [ ] `app/api/deps.py` — JWT 解析 + 角色校验依赖
  - `get_current_user()` — 解析 token，返回用户
  - `require_role("ADMIN")` — 角色守卫
- [ ] `app/models/enums/` — 角色枚举 / 状态枚举
- [ ] `app/infrastructure/llm/deepseek_client.py` — DeepSeek HTTP 客户端封装
  - chat() / vision() 两个方法
- [ ] `app/infrastructure/storage/file_store.py` — 文件本地存储
- [ ] `app/infrastructure/cache/memory_cache.py` — aiocache 封装
- [ ] Alembic 初始化 + `alembic.ini` + 首条 migration

---

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/ping` | 健康检查，返回 `{ code:200, data:"pong" }` |

---

## 产出文件

```
app/
├── main.py
├── config/settings.py
├── db/session.py
├── api/deps.py
├── api/v1/__init__.py          # 路由聚合
├── models/schemas/result.py
├── models/enums/__init__.py
├── infrastructure/llm/deepseek_client.py
├── infrastructure/storage/file_store.py
└── infrastructure/cache/memory_cache.py
alembic.ini
alembic/versions/
```

---

## 验收标准

- [ ] `uvicorn app.main:app --reload` 启动无报错
- [ ] `GET /api/ping` 返回 200 + `{ code:200, data:"pong" }`
- [ ] SQLAlchemy 能连上 KingbaseES（`SELECT 1` 通过）
- [ ] Alembic 能生成空迁移
- [ ] DeepSeek 客户端能发出测试请求并收到响应
- [ ] JWT 依赖能解析 token 并校验角色
