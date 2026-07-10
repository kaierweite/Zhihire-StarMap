# Day 05 — 能力图谱（networkx 内存图）

> **前置依赖**：Day 04（技能归一）

---

## 任务清单

- [ ] 创建 app/core/graph/skill_graph.py
  - 从 DB 加载 skill + skill_relation 构建 networkx 图
  - lifespan 启动钩子：从 DB 全量重建图
  - 支持 4 类边：PREREQUISITE / INCLUDES / SIMILAR / COMPLEMENTARY
  - 节点属性：name, category, status
- [ ] 创建 app/api/graph.py
  - POST /ai/graph/build → 返回 ECharts JSON（节点 + 边 + category 上色）
  - POST /ai/graph/reload → 从 DB 全量重建内存图
- [ ] community detection：按 skill.category 分簇
- [ ] 缺口分析：用户技能 vs 目标岗位，沿 PREREQUISITE 反推前置链
- [ ] 测试：重建图 → 查询 → 返回 ECharts JSON

---

## 验收标准

- [ ] lifespan 启动时自动重建图
- [ ] 4 类边正确渲染
- [ ] category 上色正确
- [ ] 缺口分析返回正确
