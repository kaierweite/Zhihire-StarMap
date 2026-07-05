# Day 12 — 面试模块（ADR-0011）

> **日期**：2026-07-17（周五）
> **阶段**：扩展功能
> **前置依赖**：Day 09（匹配推荐）+ Day 05（技能字典）

---

## 目标

完成模拟面试全链路：出题 → 评答 → 报告 → 简历优化。

---

## 任务清单

### 1. 面试模块实体（1h）

- [x] `InterviewSession` 实体：id, userId, jobId(可空), occupationRoleId, status(PENDING/IN_PROGRESS/COMPLETED/ABORTED), startedAt, finishedAt
- [x] `InterviewQuestion` 实体：id, sessionId, questionType(TECHNICAL/BEHAVIORAL/SITUATIONAL/RESUME_BASED), content, expectedPoints(JSONB), orderNo, isBankVisible
- [x] `InterviewAnswer` 实体：id, questionId, content, aiScore(FLOAT 0~100), aiFeedback, matchedPoints(JSONB), missedPoints(JSONB), answeredAt
- [x] `InterviewReport` 实体：id, sessionId, overallScore(FLOAT 0~100), radar(JSONB), feedback(JSONB)
- [x] `ResumeOptimization` 实体：id, resumeId, jobId(可空), suggestions(JSONB)

### 2. 模拟面试接口（2h）

- [x] `POST /api/interview/start` — 开始模拟面试
  - 创建 interview_session（status=PENDING）
  - 可传 jobId（针对特定岗位）或自动按最高 occupation_role
- `POST /api/interview/questions` — 生成面试题
  - 调 AI 服务 `POST /ai/interview/questions`
  - AI 根据 JD + 用户技能输出题目列表
  - 写入 interview_question（含 expected_points）
- `POST /api/interview/answer` — 提交回答
  - 调 AI 服务 `POST /ai/interview/evaluate`
  - AI 输出 score + feedback + matched_points + missed_points
  - 写入 interview_answer
- `POST /api/interview/report` — 生成面试报告
  - 调 AI 服务 `POST /ai/interview/report`
  - AI 汇总所有回答 + match_detail breakdown
  - 输出 radar 五维 + overall_score + feedback
  - 写入 interview_report
  - interview_question.is_bank_visible = true

### 3. 简历优化接口（1h）

- `POST /api/resume/optimize` — 生成简历优化建议
  - 入参：resumeId, jobId(可空)
  - [x] 调 AI 服务 `POST /ai/resume/optimize`
  - AI 根据 match_detail 缺口 + 简历 raw_text 输出 suggestions
  - 写入 resume_optimization
- `GET /api/resume/{id}/optimization` — 获取简历优化建议

### 4. 面试记录查询（0.5h）

- `GET /api/interview/list` — 面试记录列表（分页）
- `GET /api/interview/{sessionId}` — 面试详情（含报告）
- `GET /api/interview/question-bank` — 题库列表（is_bank_visible=true）

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/interview/` | 面试模块全套实体/Controller/Service |
| `POST /api/interview/start` | 开始模拟面试 |
| `POST /api/interview/questions` | AI 出题 |
| `POST /api/interview/answer` | 提交回答 + AI 评分 |
| `POST /api/interview/report` | 生成面试报告 |
| `POST /api/resume/optimize` | 简历优化建议 |

---

## 验收标准

- [x] 模拟面试流程：开始 → 出题 → 回答 → 评分 → 报告
- [x] 面试题按 JD + 用户技能生成，含 expected_points
- [x] 回答评分：score + matched/missed points
- [x] 报告 radar 五维与 match_detail breakdown 对齐
- [x] 题库复用：报告生成后 is_bank_visible = true
- [x] 简历优化：基于缺口 + 原文生成 suggestions
