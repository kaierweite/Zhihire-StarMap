# Zhihire StarMap（智聘星图）

基于银河麒麟操作系统的 AI 智能匹配与能力图谱平台。

> **第十五届中国软件杯大赛 B2 赛题作品**
> 出题企业：麒麟软件有限公司

---

## 项目简介

智聘星图（Zhihire StarMap）是一个基于 AI 大模型与知识图谱技术的人才智能招聘平台，部署于 **银河麒麟 V11（LoongArch）** 操作系统，使用 **人大金仓 KingbaseES** 国产数据库，AI 算力全走云端 **DeepSeek API**。

系统面向**三端用户**（求职者 / 企业 / 管理员），提供全链路招聘闭环服务：
- **求职者端** — 简历解析 → 能力图谱 → 岗位匹配 → AI 模拟面试 → 职业规划
- **企业端** — 岗位发布（JD 上传/手动）→ 候选人推荐 → 面试邀请
- **管理端** — 用户管理 / 企业审核 / 技能字典 / 数据统计 / 操作审计

---

## 核心功能

### 求职者端
- 注册登录 & 个人中心（完成度进度条 + 校友星图）
- 简历上传与 AI 解析（PDF/DOCX/DOC，技能归一 + 字典三态兜底）
- 个人能力图谱（类型化边知识图谱 + 技能缺口视图 + PREREQUISITE 前置链）
- 岗位智能推荐（四维评分：技能/经验/位置/学历，可解释依据）
- 岗位语义搜索 + 多维筛选
- AI 模拟面试（LLM 实时问答 + 即时评分 + 面试报告）
- AI 职业规划（图算法缺口分析 + 学习路线生成）

### 企业端
- 企业注册与资质审核
- 岗位发布（手动填写 / JD 智能解析双模式）
- 岗位能力图谱
- 人才智能推荐（人岗双向 4 维匹配 + 图谱增值）
- 候选人管理 + 面试邀请闭环

### 管理端
- 仪表板（数据统计聚合 + 服务状态卡片）
- 企业审核 / 用户管理（封禁+数据维护）
- 技能字典审核（候选词审核 + 同义合并）
- 操作日志审计（AOP 切面落库）

---

## 技术栈

### 架构总览

`
Vue 3 + TypeScript (三端前端)
    ↓ HTTP / JWT
FastAPI (全栈主服务，内嵌 AI 能力)
    ↓ SQLAlchemy 2.0 Async
KingbaseES (人大金仓，PostgreSQL 兼容模式)
    ↑
云端 DeepSeek API (文档解析 / 面试 / 职业规划)
`

### 前端
- Vue 3 + TypeScript + Element Plus + ECharts
- Lucide 图标 + 适配麒麟浏览器的 SCSS 样式
- 三端独立构建：user / company / admin

### 后端
- **框架：** FastAPI + SQLAlchemy 2.0（异步）+ Alembic + JWT
- **分层架构：** api/ → services/ → core/ + infrastructure/
- **AI 能力：** LLM 模拟面试 + 即时评分 + 简历优化
- **文档解析：** pdfplumber + python-docx（纯 Python，适配龙芯）
- **知识图谱：** networkx（常驻内存图，skill.category 上色）
- **缓存：** aiocache + 本地 match_result 表缓存
- **密码加密：** BCrypt（passlib）

### 数据库（共 27 张表）
- KingbaseES（PostgreSQL 兼容模式）
- 软删除标记 deleted_at（VARCHAR ''0''/''1''）
- JSONB 存储弹性结构化数据
- Alembic 管理迁移

### 部署环境
- 银河麒麟 V11 + LoongArch（龙芯，四核 / 8GB RAM / 256GB 存储）
- 裸部署（systemd），无需 Docker
- 人大金仓 KingbaseES V8（兼容 PostgreSQL 协议，端口 54321）

---

## 项目结构

`
Zhihire-StarMap/
├── frontend/                # Vue 3 三端前端
│   └── src/
│       ├── views/user/      # 求职者页面
│       ├── views/company/   # 企业页面
│       ├── views/admin/     # 管理员页面
│       └── ...
├── backend/                 # FastAPI 全栈后端
│   └── app/
│       ├── api/v1/          # 路由层
│       ├── services/        # 业务编排层
│       ├── core/            # 核心算法（解析/匹配/图谱）
│       ├── infrastructure/  # LLM / 缓存 / 文件
│       ├── models/          # ORM / Pydantic / 枚举
│       ├── repositories/    # 原子数据库操作
│       ├── config/          # 配置管理
│       ├── db/              # 连接与会话管理
│       └── main.py          # 应用入口
├── database/                # ER 图 / 建表 SQL / 种子数据
├── docs/                    # 比赛文档 & 架构决策记录
├── prototype/               # HTML 富原型（27 个页面）
├── deploy/                  # 部署脚本与配置
├── scripts/                 # 工具脚本
├── test/                    # 测试数据与夹具
└── start_all.bat            # 本地开发一键启动
`

---

## 本地开发

### 前置依赖
- Python 3.11+
- Node.js 18+
- KingbaseES（或 PostgreSQL 兼容数据库，端口 54321）

### 启动步骤

`ash
# 1. 启动数据库
#    确保 127.0.0.1:54321 可访问

# 2. 初始化数据库
cd backend
pip install -r requirements.txt
alembic upgrade head

# 3. 启动后端
python run.py
# 后端运行在 http://127.0.0.1:8000

# 4. 启动前端（三端）
cd frontend
npm install
npm run dev         # 用户端 http://localhost:5173
npx vite --port 5174  # 企业端 http://localhost:5174
npx vite --port 5175  # 管理端 http://localhost:5175
`

### 快速启动（Windows）
`ash
start_all.bat
`

---

## 开发规范

- 后端统一使用 Result[T] Pydantic 模型封装返回
- 遵循 RESTful API 设计规范（前缀 /api/）
- 状态字段使用 VARCHAR 语义化枚举（NORMAL/DISABLED/BANNED）
- 密码使用 BCrypt 加密
- 四层后端分层：api/ -> services/ -> core/ + infrastructure/
- Git 提交格式：[type]: [description]

---

## 许可证

仅用于第十五届中国软件杯大赛参赛作品。
