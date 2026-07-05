# Day 03 — 求职者端布局 + 个人中心

> **前置依赖**：Day 02（路由 + 登录）

---

## 目标

完成求职者端统一布局（导航栏 + 侧边栏）、个人中心页面。

---

## 任务清单

- [ ] 创建 components/AppHeader.vue（统一导航栏：探索/职位推荐/职位搜索/简历中心/面试功能/社交 + 通知铃铛）
- [ ] 创建 components/AppSidebar.vue（求职者端侧边栏）
- [ ] 创建 layout/UserLayout.vue（导航栏 + 侧边栏 + 内容区）
- [ ] 创建 views/user/Profile.vue（个人中心：城市选择器 + 完成度进度条 + 基本资料）
- [ ] 对接 API：GET /api/user/profile、PUT /api/user/profile
- [ ] 实现通知铃铛未读数轮询（GET /api/notification/unread-count 每 30s）

---

## 验收标准

- [ ] 导航栏在所有 user 页面一致
- [ ] 当前页面导航项高亮
- [ ] 个人中心显示用户信息 + 完成度
