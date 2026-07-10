# Day 06 — 可解释匹配评分

> **前置依赖**：Day 05（图谱）

---

## 任务清单

- [ ] 创建 app/core/recommender/matcher.py
  - 计算四维子分：技能(importance 加权) / 学历(档差) / 经验(年限比例) / 城市(契合度)
  - 向量仅做候选召回 + 同义增强，不打主分
  - INCLUDES 父子归一：JD 要父、用户会子 → 0.6 * required_level_weight
  - 图增值：community detection → 相近领域；PREREQUISITE → 学习前置链
  - 模板拼接 rationale + graph_hints
- [ ] 创建 app/api/recommend.py
  - POST /ai/recommend/match → 入参 user_skills + candidates(≤50)，出参 match_results
- [ ] match_detail 固定结构：{score, breakdown{skill/edu/exp/city}, rationale, graph_hints}
- [ ] 测试：用演示数据验证评分结果

---

## 验收标准

- [ ] 四维子分计算正确
- [ ] rationale 模板拼接输出
- [ ] graph_hints 图路径建议输出
- [ ] 向量不作为主分
