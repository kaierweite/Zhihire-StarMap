# Day 08 — 面试模块（出题 + 评答 + 报告）

> **前置依赖**：Day 07（职业规划）

---

## 任务清单

- [ ] 创建 app/api/interview.py
  - POST /ai/interview/questions → 据 JD + 用户技能出题
  - POST /ai/interview/evaluate → 评答：score + feedback + matched/missed points
  - POST /ai/interview/report → 汇总：overall_score + radar 五维 + feedback
- [ ] 出题 prompt 设计：4 类题型（TECHNICAL/BEHAVIORAL/SITUATIONAL/RESUME_BASED）
- [ ] 评答 prompt 设计：对照 expected_points 逐条评分
- [ ] 报告 prompt 设计：汇总 + radar 与 match_detail breakdown 对齐
- [ ] 创建 app/api/resume_optimize.py
  - POST /ai/resume/optimize → 据 match_detail 缺口 + 简历原文生成 suggestions
- [ ] 测试：模拟面试全流程

---

## 验收标准

- [ ] 出题按 JD + 用户技能生成
- [ ] 评答输出 score + matched/missed points
- [ ] 报告 radar 五维与 match_detail 对齐
- [ ] 简历优化 suggestions 格式正确