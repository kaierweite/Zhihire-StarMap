# Day 06 — 职位推荐 + 可解释面板

> **前置依赖**：Day 05（图谱）

---

## 目标

完成岗位推荐列表 + 四维子分 + 匹配依据 + 投递功能。

---

## 任务清单

- [ ] 创建 views/user/JobRecommend.vue（岗位推荐页）
- [ ] 推荐卡片：匹配度环 + 基本信息 + 四维子分条（技能/学历/经验/城市）
- [ ] 匹配依据文本 + 图谱学习建议
- [ ] 分页组件（el-pagination）
- [ ] 投递按钮 → POST /api/recommend/job/{jobId}/apply
- [ ] 对接 API：GET /api/recommend/jobs?page=&size=

---

## 验收标准

- [ ] 推荐列表分页正常
- [ ] 四维子分可视化展示
- [ ] 投递后提示成功
