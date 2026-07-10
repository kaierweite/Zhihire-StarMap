# Day 08 — Interview AI 面试模块

> **前置依赖**：day00 LLM 客户端 + day03 简历解析
> **前端对应**：InterviewHome.vue / InterviewChat.vue / InterviewReport.vue / InterviewPhone.vue / InterviewVideo.vue / QuestionBank.vue / ResumeOptimize.vue
> **核心 ADR**：ADR-0011（面试培养模块）

---

## 目标

AI 模拟面试官 + 即时评分 + 面试报告 + 题库 + 简历优化。
本期望只做文本链路（聊天式），语音/视频标为愿景不演示。

---

## 涉及数据表

- `interview_session` — 面试会话（user_id, job_id 可空, occupation_role_id, status, created_at）
- `interview_question` — 面试题（session_id, question_type, content, expected_points JSONB, is_bank_visible）
- `interview_answer` — 回答（question_id, content, ai_score, ai_feedback）
- `interview_report` — 报告（session_id, overall_score, radar JSONB, feedback JSONB）
- `resume_optimization` — 简历优化建议（resume_id, job_id, suggestions JSONB）

---

## AI 编排（四条链路全走云端 DeepSeek）

1. **简历解析** — 已有（day03）
2. **匹配评分** — 已有（day06 可解释子分）
3. **模拟面试问答**（新增）
   - 出题：`POST /ai/interview/questions` 入参 `{session_id, job_id, resume_id, count}`
   - 评答：`POST /ai/interview/evaluate` 入参 `{question_id, answer}`
   - 报告：`POST /ai/interview/report` 入参 `{session_id}`
4. **简历优化** — 已有（day03 的 optimize 端点）

---

## API 清单

### 1. POST `/api/interview/start`

- 需要 USER 角色
| 参数 | 类型 | 说明 |
|------|------|------|
| job_id | int | 目标岗位（可为空，按 role 推） |
| occupation_role_id | int | 职业角色 |

- 创建 interview_session（status=IN_PROGRESS）
- 调 DeepSeek 按 JD + 用户技能生成第一题
- 写 interview_question
- 返回 `Result<{ session_id, first_question }>`

### 2. POST `/api/interview/message`

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | int | 会话 ID |
| question_id | int | 当前题目 ID |
| answer | string | 用户回答 |

- 调 DeepSeek 评分：`{score, feedback, matched_points[], missed_points[]}`
- 写 interview_answer
- 判断是否结束（>=maxQuestions）
  - 否 → AI 生成下一题 → 返回
  - 是 → 触发报告生成 → 返回结束标记
- 返回 `Result<{ next_question?, overall_score?, is_finished }>`

### 3. GET `/api/interview/report/{session_id}`

- 面试报告：overall_score + radar 五维（technical/communication/problem_solving/culture_fit/depth）+ feedback
- radar 维度对齐 match_detail breakdown：
  - technical 吸收 skill 子分
  - communication / problem_solving 由 AI 问答评分产出
  - culture_fit 由 JD 关键词 + 回答匹配
  - depth 由 PREREQUISITE 链深度推断
- 返回 `Result<InterviewReportVO>`

### 4. GET `/api/interview/question-bank`

| 参数 | 类型 | 说明 |
|------|------|------|
| job_id | int | 按岗位筛选 |
| role | string | 按角色筛选 |
| type | string | 题目类型 |
| page/size | int | 分页 |

- 查 `interview_question` where `is_bank_visible=true`
- 返回 `Result<PageData<QuestionVO>>`

---

## 代码分层

| 层 | 文件 |
|----|------|
| 路由 | `api/v1/interview.py` |
| 服务 | `services/interview_service.py` |
| 核心 | `core/parsing/` — 面试出题/评答 prompt 模板 |
| 仓储 | `repositories/interview_repository.py` |

---

## 验收标准

- [ ] 开始面试 → 返回第一题
- [ ] 逐题回答 → AI 评分 + 下一题
- [ ] 最后一题 → 报告生成 → 前端跳转报告页
- [ ] 报告含五维雷达图
- [ ] 题库页可按岗位/角色筛选
