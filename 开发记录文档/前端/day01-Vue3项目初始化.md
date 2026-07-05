# Day 01 — Vue 3 项目初始化

> **日期**：与后端 day05 并行
> **阶段**：基础搭建
> **前置依赖**：Node.js 18+ 已安装

---

## 目标

完成 Vue 3 + TypeScript + Element Plus + Vue Router + Pinia + Axios 项目骨架搭建。

---

## 任务清单

- [ ] 使用 Vite 创建 Vue 3 + TypeScript 项目
  ```bash
  npm create vite@latest frontend -- --template vue-ts
  cd frontend
  npm install
  ```
- [ ] 安装核心依赖
  ```bash
  npm install element-plus @element-plus/icons-vue
  npm install vue-router@4 pinia axios echarts
  npm install -D @types/node unplugin-auto-import unplugin-vue-components sass
  ```
- [ ] 配置 Element Plus 按需导入（unplugin-vue-components）
- [ ] 配置 vite.config.ts（别名 @ → src、代理 /api → localhost:8080）
- [ ] 创建目录结构：api / views / router / store / components / styles / utils
- [ ] 创建全局样式 styles/global.scss（导入设计令牌 colors）
- [ ] 创建 Axios 封装 utils/request.ts（请求拦截器加 token、响应拦截器统一错误处理）
- [ ] 创建 App.vue 基础布局

---

## 产出物

| 产出 | 说明 |
|------|------|
| `frontend/` | Vue 3 + TypeScript 项目 |
| `vite.config.ts` | 构建配置 + API 代理 |
| `src/utils/request.ts` | Axios 封装 |
| `src/styles/global.scss` | 全局样式 |

---

## 验收标准

- [ ] `npm run dev` 启动无报错
- [ ] 浏览器访问 localhost:5173 显示空白页
- [ ] Element Plus 组件可正常使用
