# 智聘星图后端（FastAPI 主服务，含 AI 能力）

> 冒烟骨架待启动。详见 `开发记录文档/后端/day00-基础设施.md`。
> AI 能力（文档解析 / 知识图谱 / 推荐算法）内置于本主服务，不再独立部署。

## 目录结构

```
backend/
└── app/
    ├── main.py                 # FastAPI 入口（CORS + 异常处理 + 路由挂载）
    ├── config/                 # Pydantic Settings 配置
    ├── db/                     # async engine + AsyncSessionLocal
    ├── api/
    │   ├── deps.py             # JWT 解析 + require_role 角色守卫
    │   └── v1/                 # 路由层（参数校验 + 响应封装）
    ├── services/               # 业务服务层（编排 core + infrastructure）
    ├── core/                   # 核心算法层（parsing / normalize / graph / matching / career）
    ├── infrastructure/         # 基础设施防腐层（llm / cache / storage）
    ├── models/
    │   ├── entities/           # SQLAlchemy ORM
    │   ├── schemas/            # Pydantic 模型 + Result[T]
    │   └── enums/              # 角色与状态枚举
    └── repositories/           # 仓储层（原子数据库操作）
```

## 技术栈

- FastAPI + Uvicorn + SQLAlchemy 2.0（async）+ Alembic
- JWT：python-jose；密码：passlib（bcrypt）；缓存：aiocache
- AI：云端 DeepSeek API（chat + vision），客户端封装在 `infrastructure/llm/`
- 文档解析：pdfplumber + python-docx（纯 Python，适配龙芯）
- 知识图谱：networkx（常驻内存图）
- KingbaseES（国产数据库，PostgreSQL 兼容，asyncpg 驱动）
