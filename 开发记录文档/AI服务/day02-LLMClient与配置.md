# Day 02 — LLMClient + DeepSeek 配置

> **前置依赖**：Day 01（项目骨架）

---

## 任务清单

- [ ] 创建 app/core/llm_client.py（DeepSeek API 调用封装）
  - async def chat(prompt, system_prompt=None) → str
  - async def chat_json(prompt, system_prompt=None) → dict（强制 JSON 输出）
  - 超时 30s，重试 2 次
  - 错误处理：API 不可用时返回降级提示
- [ ] 创建 app/models/schemas.py（Pydantic 数据模型）
  - ResumeParseResult, JobParseResult
  - MatchResult, MatchBreakdown
  - CareerPlanResult
  - InterviewQuestion, InterviewAnswer, InterviewReport
  - ResumeOptimization
- [ ] 测试：调用 DeepSeek API 返回正常响应

---

## 验收标准

- [ ] LLMClient 可正常调用 DeepSeek API
- [ ] JSON 输出模式可用
- [ ] 超时和重试机制生效
