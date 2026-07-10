# 智聘星图前端（Vue 3 + TypeScript）

中国软件杯 B2 赛题 — AI 智能匹配与能力图谱 + 面试能力培养平台

## 技术栈

- **框架：** Vue 3 + TypeScript + Composition API（`<script setup>`）
- **构建：** Vite 6
- **UI：** Element Plus（按需导入 via unplugin）
- **图表：** ECharts 5
- **路由：** Vue Router 4 + 角色守卫（ADMIN / USER / COMPANY）
- **状态：** Pinia
- **HTTP：** Axios + 统一拦截器
- **图标：** Lucide Vue Next
- **样式：** SCSS + 设计令牌（主色 #1A3A5C / 辅助色 #0EA5E9）

## 快速开始

```bash
cd frontend
npm install --registry https://registry.npmmirror.com
npm run dev
```

开发服务器默认 `http://localhost:5173`，`/api` 请求代理到 `http://localhost:8080`。

## 目录结构

```
src/
├── api/              # API 接口封装
├── views/
│   ├── common/       # 首页、登录、注册
│   ├── user/         # 求职者端（17 个页面）
│   ├── company/      # 企业端（6 个页面）
│   └── admin/        # 管理端（4 个页面）
├── router/           # 路由配置 + 角色守卫
├── store/            # Pinia 状态管理
├── components/       # 通用组件
├── styles/           # 全局样式 + 设计令牌
├── types/            # TypeScript 类型定义
├── utils/            # 工具函数（Axios 封装）
├── App.vue
└── main.ts
```

## 后端 API 对接

已完成封装：`POST /api/auth/register`、`POST /api/auth/login`、`GET /api/ping`
