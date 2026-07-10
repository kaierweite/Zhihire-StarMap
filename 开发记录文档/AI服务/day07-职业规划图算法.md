# Day 07 — 职业规划（图算法 + LLM 润色）

> **前置依赖**：Day 06（匹配评分）

---

## 任务清单

- [ ] 创建 app/core/graph/career_planner.py
  - 缺口集 = 目标 role 的 MUST 技能 - 用户已有
  - 沿 PREREQUISITE 边拓扑排序 → 有序学习路径
  - LLM 仅润色：把 {gap, path, target_role} 喂 DeepSeek 输出通顺话
  - 不改结构化结果，分数/路径不经大模型
- [ ] 创建 app/api/career.py
  - POST /ai/career/analyze → {gap_skills[], learning_path[], graph_hints, rationale, llm_text}
- [ ] 测试：用演示数据验证规划结果

---

## 验收标准

- [ ] 缺口集计算正确
- [ ] 学习路径拓扑排序有序
- [ ] LLM 仅润色不改结构