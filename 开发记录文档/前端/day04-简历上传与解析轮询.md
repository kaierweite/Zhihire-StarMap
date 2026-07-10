# Day 04 — 简历上传 + 解析轮询

> **前置依赖**：Day 03（布局）

---

## 目标

完成简历上传、解析进度轮询、解析结果展示。

---

## 任务清单

- [x] 创建 views/user/ResumeCenter.vue（简历中心页）
- [x] 实现文件上传组件（el-upload，限制 PDF/DOC/DOCX，≤10MB）
- [x] 上传后创建 parse_task，显示解析进度条
- [x] 轮询 GET /api/parse/task/{id}（间隔 2s，超 30s 提示）
- [x] 解析完成后展示结构化结果：技能标签 + 工作经历 + 教育背景
- [x] 解析失败/拒绝时标红 + 「重新解析」按钮
- [x] 对接 API：POST /api/resume/upload、GET /api/parse/task/{id}

---

## 验收标准

- [x] 文件类型和大小校验生效
- [x] 上传后显示解析进度
- [x] 解析完成展示技能/经历/教育
