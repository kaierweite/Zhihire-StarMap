# Day 05 — 能力图谱 + ECharts

> **前置依赖**：Day 04（解析结果）

---

## 目标

完成能力图谱页面，ECharts 渲染知识图谱 + 缺口分析。

---

## 任务清单

- [x] 创建 views/user/SkillGraph.vue（能力图谱页）
- [x] ECharts 关系图渲染：技能节点 + 4 类边（PREREQUISITE/INCLUDES/SIMILAR/COMPLEMENTARY）
- [x] 节点按 category 上色（后端/前端/测试/运维/数据/通用）
- [x] 缺口分析 Tab：当前技能 vs 目标岗位对比
- [x] 覆盖率进度条 + AI 建议
- [x] 对接 API：GET /api/graph/user/{userId}、GET /api/graph/gap/{userId}/{jobId}

---

## 验收标准

- [x] 图谱节点和边正确渲染
- [x] 缺口技能标红
- [x] 覆盖率百分比正确
