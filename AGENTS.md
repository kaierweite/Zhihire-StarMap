# 智聘星图 (Zhihire StarMap) — 开发规范

> 本项目使用 Codex 进行 AI 辅助开发，本文档定义了开发规范和约束条件。

## 项目定位

第十五届中国软件杯大赛 B2 赛题作品，基于银河麒麟操作系统的 AI 智能匹配与能力图谱 + 面试能力培养平台。

## 技术栈

- **前端：** Vue 3 + TypeScript + Element Plus + ECharts
- **后端（全栈）：** FastAPI + SQLAlchemy 2.0 (async) + Alembic + JWT (python-jose) + aiocache
- **数据库：** 人大金仓 KingbaseES（国产数据库，兼容 PostgreSQL）
- **AI 能力：** 云端 DeepSeek API（内置于主服务，不再独立部署）
- **AI 面试：** LLM 模拟面试官 + 即时评分 + 面试报告 + 简历优化（ADR-0011）
- **文档解析：** pdfplumber + python-docx（纯 Python，适配龙芯）
- **知识图谱：** networkx（常驻内存图，skill.category 上色）
- **部署：** 银河麒麟 V11 + LoongArch（龙芯）

## 开发规范

### 分支策略
- `main` — 稳定分支，所有开发完成后合并
- 如有多人协作，使用 `dev` 分支进行日常开发

### Git 提交规范
- 提交信息格式：`[type]: [description]`
- type 包括：feat/fix/docs/refactor/test/chore
- 每天至少提交一次

### 代码质量
- 后端统一使用 `Result[T]` Pydantic 模型封装返回
- 遵循 RESTful API 设计规范
- 状态字段使用 VARCHAR 语义化枚举（NORMAL/DISABLED/BANNED）
- API 路径前缀：`/api/`
- 密码使用 BCrypt 加密（passlib）

### 数据库规范
- 使用 KingbaseES（PostgreSQL 兼容模式）
- 表名使用小写蛇形命名
- 所有表包含 `created_at` / `updated_at` / `deleted_at` 时间字段
- JSONB 存储弹性结构化数据
- 状态字段使用 VARCHAR 而非 INT
- 共 27 张表（22 基础 + 5 面试模块，ADR-0011）
- 迁移工具：Alembic

### 后端分层规范（FastAPI）
- `api/` — 路由层，只做参数校验和响应封装
- `services/` — 业务服务层，编排 core + infrastructure
- `core/` — 核心算法层，无外部依赖（解析/归一/图谱/匹配）
- `infrastructure/` — 基础设施层，外部依赖防腐（LLM / 缓存 / 文件）
- `models/` — Pydantic 模型 + SQLAlchemy ORM + 枚举
- `repositories/` — 仓储层，只做原子数据库操作

## 项目目录结构

| 代码类型 | 位置 |
|---------|------|
| Python/FastAPI | `backend/app/api/` |
| 业务服务 | `backend/app/services/` |
| 核心算法 | `backend/app/core/` |
| 基础设施 | `backend/app/infrastructure/` |
| ORM/模型/枚举 | `backend/app/models/` |
| 数据仓储 | `backend/app/repositories/` |
