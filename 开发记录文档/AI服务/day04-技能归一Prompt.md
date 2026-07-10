# Day 04 — 技能归一 Prompt

> **前置依赖**：Day 03（文档解析）

---

## 任务清单

- [ ] 创建 app/core/normalizer/skill_normalizer.py
  - build_prompt(raw_skills, dictionary_subset) → str
  - 输出格式：[{raw, canonical_name, confidence}]
  - 动态注入：从后端获取 top-30 字典子集注入 prompt
- [ ] Prompt 设计要点：
  - 输入：原始技能文本列表 + 字典候选名列表
  - 输出：强制 JSON 格式
  - 规则：优先匹配字典名，未命中则输出最接近的标准名
- [ ] 创建 /ai/parse/resume 的技能归一调用链
- [ ] 测试：用演示简历验证归一结果（SpringBoot→Spring Boot 置信度 0.9）

---

## 验收标准

- [ ] 归一输出格式正确
- [ ] 字典匹配优先
- [ ] 演示简历技能归一结果正确
