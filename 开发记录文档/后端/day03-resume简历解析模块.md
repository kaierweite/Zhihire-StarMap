# Day 03 — Resume 简历与文档解析模块

> **前置依赖**：day01 auth + day00 LLM 客户端
> **前端对应**：ResumeCenter.vue / ResumeOptimize.vue
> **核心 ADR**：ADR-0003（解析归一产出约定）

---

## 目标

用户上传简历文件（PDF/Word/含图片），系统解析提取结构化数据，技能归一入库，前端轮询解析进度。
这是整个系统的数据入口，后续能力图谱和匹配都依赖这一步。

---

## 涉及数据表

- `upload_file` — 文件唯一事实源（file_id, original_name, storage_path, mime_type, size, created_at）
- `resume` — 简历表（user_id, file_id, parse_status, parsed_data JSONB, raw_text, embedding_cache）
- `parse_task` — 解析任务表（file_id, status, progress, result, error_msg）
- `user_skill` — 技能关联（解析结果写入）
- `skill` — 技能字典（归一查表 + CANDIDATE 入库）
- `skill_synonym` — 同义词表

---

## 解析链路

```
用户上传文件
  → 存储 upload_file
  → 创建 resume（file_id 引用）+ parse_task（WAITING）
  → BackgroundTasks 异步:
      1. pdfplumber / python-docx 提取文本 + 图片帧
      2. 纯文本 → DeepSeek chat（结构化抽取 JSON）
      3. 图片帧 → DeepSeek vision（OCR）→ 合并文本流
      4. 合并文本 → DeepSeek chat（统一结构化输出）
      5. 技能归一: 按 canonical_name 查 skill 表
         命中 → 复用 skill_id，写入 user_skill
         未命中 → skill.status=CANDIDATE 入库
      6. 写回 resume.parsed_data + resume.raw_text
      7. parse_task.status=SUCCESS
  → 前端轮询 parse_task 状态
```

---

## API 清单

### 1. POST `/api/resume/upload`

- 需要 USER 角色
- multipart/form-data，接收 file 字段
- 校验：PDF/DOC/DOCX，<=10MB
- 同步：存文件 + 建 resume + 建 parse_task + 启动 BackgroundTasks
- 返回 `Result<{ resume_id, task_id }>`

### 2. GET `/api/parse/task/{task_id}`

- 前端每 2s 轮询
- 返回 `Result<{ status, progress, error_msg }>`
- status: WAITING / PARSING / SUCCESS / FAILED

### 3. GET `/api/resume`

- 需要 USER 角色
- 返回当前用户简历列表 `Result<PageData<ResumeVO>>`

### 4. GET `/api/resume/{resume_id}`

- 返回简历详情 + 解析结果 `Result<ResumeDetailVO>`
- parsed_data 结构：name, education, years, targetJob, city, skills[], experience[]

### 5. PUT `/api/resume/{resume_id}`

- 用户修正解析结果（技能增删、经历编辑）
- 更新后标记 resume 需重算匹配
- 返回 `Result<ResumeDetailVO>`

### 6. DELETE `/api/resume/{resume_id}`

- 软删除（deleted_at），不删物理文件
- 返回 `Result[null]`

### 7. POST `/api/resume/optimize`

- 需要 USER 角色
| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 简历 ID |
| job_id | int | 目标岗位 ID（可为空，通用优化） |

- 调 DeepSeek，基于 match_detail 缺口 + raw_text 产出优化建议
- 写入 `resume_optimization` 表
- 返回 `Result<{ suggestions: [{ section, current, suggestion, relates_to_skill }] }>`

---

## 代码分层

| 层 | 文件 | 职责 |
|----|------|------|
| 路由 | `api/v1/resume.py` | 上传/轮询/CRUD |
| 路由 | `api/v1/parse.py` | 解析任务轮询 |
| 服务 | `services/resume_service.py` | 上传编排 |
| 服务 | `services/parse_service.py` | 异步解析流程 |
| 核心 | `core/parsing/extractor.py` | pdfplumber/python-docx 文本提取 |
| 核心 | `core/normalize/skill_normalizer.py` | 技能归一查表 |
| 基础设施 | `infrastructure/llm/deepseek_client.py` | chat() + vision() |
| 仓储 | `repositories/resume_repository.py` | |
| 仓储 | `repositories/parse_task_repository.py` | |
| 仓储 | `repositories/skill_repository.py` | |

---

## 验收标准

- [ ] 上传 PDF → 返回 resume_id + task_id
- [ ] 轮询 task → PARSING → SUCCESS
- [ ] GET resume/{id} 返回结构化数据（姓名/技能/经历）
- [ ] 技能归一：已知技能命中 skill_id，未知技能进 CANDIDATE
- [ ] PDF 含图片页 → vision OCR 路径跑通
- [ ] PUT 编辑简历 → 数据更新
- [ ] POST optimize → 返回 AI 优化建议
