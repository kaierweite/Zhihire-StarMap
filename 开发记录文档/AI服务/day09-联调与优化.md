# Day 09 — 联调 + 性能优化

> **前置依赖**：Day 08（面试模块）

---

## 任务清单

- [ ] 与后端 Spring Boot 全链路联调
  - 后端调 /ai/parse/resume → AI 返回 → 后端写库
  - 后端调 /ai/recommend/match → AI 返回 → 后端写 match_result
  - 后端调 /ai/career/analyze → AI 返回 → 后端写 career_plan
  - 后端调 /ai/interview/* → AI 返回 → 后端写面试数据
- [ ] 性能优化：
  - 文档解析：大文件分块处理
  - LLM 调用：并发请求控制
  - networkx 图：查询缓存
- [ ] 错误处理：LLM 超时降级、API 不可用提示
- [ ] 日志：关键操作记录日志

---

## 验收标准

- [ ] 后端调 AI 服务全链路通过
- [ ] LLM 超时有降级处理
- [ ] 响应时间合理