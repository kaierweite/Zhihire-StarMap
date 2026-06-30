# 智聘星图 (Zhihire StarMap) — 开发规范

> 本项目使用 Codex CLI 进行 AI 辅助开发，本文档定义了开发规范和约束条件。

## 项目定位

第十五届中国软件杯大赛 B2 赛题作品，基于银河麒麟操作系统的 AI 智能匹配与能力图谱平台。

## 技术栈

- **前端：** Vue 3 + TypeScript + Element Plus + ECharts + Vite + Pinia + Axios
- **后端（主服务）：** Java 21 + Spring Boot 3 + MyBatis-Plus + KingbaseES + Redis + JWT + Knife4j
- **AI 微服务：** Python 3.12 + FastAPI + LangChain + DeepSeek API + sentence-transformers
- **文档解析：** docling + pdfplumber + python-docx
- **能力图谱：** networkx + scikit-learn + ECharts Graph

## 开发规范

### 分支策略
- `main` — 稳定分支，所有开发完成后合并
- 如有多人协作，使用 `dev` 分支进行日常开发

### Git 提交规范
- 提交信息格式：`[type]: [description]`
- type 包括：feat/fix/docs/refactor/test/chore
- 每天至少提交一次

### 代码质量
- 后端统一使用 `Result<T>` 封装返回
- 遵循 RESTful API 设计规范
- 状态字段使用 VARCHAR 语义化枚举（NORMAL/DISABLED/BANNED）
- API 路径前缀：`/api/`
- 密码使用 BCrypt 加密

### 数据库规范
- 使用 KingbaseES（PostgreSQL 兼容模式）
- 表名使用小写蛇形命名
- 所有表包含 `created_at` / `updated_at` / `deleted_at` 时间字段
- JSONB 存储弹性结构化数据
- 状态字段使用 VARCHAR 而非 INT

## 项目目录结构

```
Zhihire-StarMap/
├── frontend/          # Vue3 前端
├── backend/           # Spring Boot 主服务
├── ai-service/        # FastAPI AI 微服务
├── database/          # 数据库(ER/建表SQL/种子数据)
├── docs/              # 比赛文档
├── prototype/         # 原型图(draw.io)
├── assets/            # 资源文件
├── deploy/            # 部署配置
├── scripts/           # 工具脚本
├── test/              # 测试数据
├── ppt/               # 演示PPT
├── video/             # 演示视频
└── task/              # 任务开发记录
```

## 各技术栈文件位置

| 代码类型 | 位置 |
|---------|------|
| Java/Spring Boot | `backend/src/main/java/com/zhihire/starmap/` |
| Vue3/TypeScript | `frontend/src/` |
| Python/FastAPI | `ai-service/app/` |
| SQL | `database/` |
| 部署脚本 | `deploy/` |
