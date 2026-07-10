# Day 02 — 路由 + 登录注册页

> **前置依赖**：Day 01（项目骨架）

---

## 目标

完成路由配置（角色守卫）、登录/注册页面。

---

## 任务清单

- [x] 创建 router/index.ts（路由表 + 角色守卫）
  - 未登录 → /login
  - USER 角色 → /user/* 路由
  - COMPANY 角色 → /company/* 路由
  - ADMIN 角色 → /admin/* 路由
- [x] 创建 store/user.ts（Pinia：token / role / userInfo）
- [x] 创建 views/common/Login.vue（双角色登录）
- [x] 创建 views/common/Register.vue（求职者 + 企业双角色注册）
- [x] 创建 views/common/Landing.vue（首页着陆页骨架）
- [x] 对接 API：POST /api/auth/login、POST /api/auth/register
- [x] 登录成功后 token 存 localStorage + Pinia，跳转对应角色首页

---

## 验收标准

- [x] 未登录访问任意页面 → 跳转 /login
- [x] 登录后根据角色跳转不同首页
- [x] JWT token 正确存储和携带
