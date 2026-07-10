# Day 12 — 管理端

> **前置依赖**：Day 11

---

## 任务清单

- [x] 创建 layout/AdminLayout.vue（管理端导航栏 + 侧边栏）
- [x] 创建 views/admin/Dashboard.vue（仪表板：数据统计 ECharts + 服务状态卡片）
- [x] 创建 views/admin/AuditManage.vue（审核管理：企业审核 Tab + 技能字典审核 Tab）
- [x] 创建 views/admin/UserManage.vue（用户管理：列表 + 搜索 + 封禁 + 岗位下架）
- [x] 创建 views/admin/SystemLog.vue（系统日志：操作日志 + 登录日志查询）
- [x] 对接 API：GET /api/admin/stat、PUT /api/admin/company/{id}/audit、GET /api/admin/logs

---

## 验收标准

- [x] 仪表板统计图表正确
- [x] 企业审核流程正常
- [x] 技能字典审核 + 同义合并正常
