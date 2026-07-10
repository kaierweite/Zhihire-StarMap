# Day 03 — 文档解析（简历 + JD）

> **前置依赖**：Day 02（LLMClient）

---

## 任务清单

- [ ] 创建 app/core/parser/document_parser.py
  - parse_pdf(file_path) → raw_text
  - parse_docx(file_path) → raw_text
  - 文件类型检测（扩展名 + 魔数）
- [ ] 创建 app/api/parse.py
  - POST /ai/parse/resume → 调 LLM 提取技能/经历/教育
  - POST /ai/parse/job → 调 LLM 提取技能要求/occupation_role_name
- [ ] Prompt 设计：
  - 简历解析 prompt：输出 {skills[{raw, canonical_name, confidence}], experience[], education, summary}
  - JD 解析 prompt：输出 {skills[{raw, canonical_name, required_level, importance}], occupation_role_name, requirements}
- [ ] 测试：用测试 PDF/DOCX 验证解析结果

---

## 验收标准

- [ ] PDF 解析返回正确 raw_text
- [ ] DOCX 解析返回正确 raw_text
- [ ] LLM 输出结构化 JSON
- [ ] 技能归一名格式正确
