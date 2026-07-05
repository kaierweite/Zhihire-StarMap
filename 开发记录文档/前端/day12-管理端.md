# Day 12 — 管理端

> **前置依赖**：Day 11

---

## 任务清单

- [ ] 创建 layout/AdminLayout.vue（管理端导航栏 + 侧边栏）
- [ ] 创建 views/admin/Dashboard.vue（仪表板：数据统计 ECharts + 服务状态卡片）
- [ ] 创建 views/admin/AuditManage.vue（审核管理：企业审核 Tab + 技能字典审核 Tab）
- [ ] 创建 views/admin/UserManage.vue（用户管理：列表 + 搜索 + 封禁 + 岗位下架）
- [ ] 创建 views/admin/SystemLog.vue（系统日志：操作日志 + 登录日志查询）
- [ ] 对接 API：GET /api/admin/stat、PUT /api/admin/company/{id}/audit、GET /api/admin/logs

---

## 验收标准

- [ ] 仪表板统计图表正确
- [ ] 企业审核流程正常
- [ ] 技能字典审核 + 同义合并正常
