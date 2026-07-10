# Day 06 — Match 双向匹配与推荐模块

> **前置依赖**：day03 简历 + day04 图谱 + day05 岗位
> **前端对应**：JobRecommend.vue / CandidateRecommend.vue / SmartScreening.vue / JobDetail.vue
> **核心 ADR**：ADR-0005（可解释子分 + 双向共用 + 图算法增值）

---

## 目标

为求职者推荐岗位，为企业推荐候选人。主分由可解释维度子分算法计算（非大模型编），图谱路径增强，双向共用一张 match_result 表。

---

## 涉及数据表

- `match_result` — 匹配结果（resume_id, job_id, score, match_detail JSONB, updated_at, is_stale）
- `recommend_record` — 推荐记录（user_id/resume_id, job_id, recommend_type: JOB/TALENT, is_clicked, is_applied, is_invited）
- `user_skill` / `job_skill` — 技能对比数据源
- `skill_relation` — 图谱增值路径
- `user_profile` — 城市/意向数据

---

## 匹配算法（三层）

### 第一层：召回
- SQL 按城市/学历/技能同义扩展召回候选集（<=50 对）
- 向量余弦相似度可选作为召回辅助（云端 embedding 或 BM25 兜底）

### 第二层：维度打分（主分）

| 维度 | 权重 | 算法 |
|------|------|------|
| 技能 | 可调(默认~40%) | job_skill.importance 加权命中率；MUST=5/NICE=3/BONUS=1；加分项按 0.6*权重；CANDIDATE 按 confidence*权重 |
| 学历 | 可调(默认~20%) | 档差评分：达标=满分，超一格+，低一档打折 |
| 经验 | 可调(默认~20%) | 年限比例，封顶 100 |
| 城市 | 可调(默认~20%) | 意向城市含岗位城市=满分，否则降级 |

主分 = 加权求和，权重可配置。

### 第三层：图谱增值
- SIMILAR 边相近技能小幅加分（用户会 Vue 3，岗位要 React）
- PREREQUISITE 边反推（用户会 Java，岗位要 Spring Boot → 有前置基础）

### match_detail JSONB 结构

```json
{
  "score": 87,
  "breakdown": {
    "skill": { "score": 8.7, "hit": ["Vue 3","TypeScript"], "miss": ["Kafka"], "detail": "命中 8/10 必备，缺 1 加分" },
    "edu": { "score": 10, "detail": "硕士，达标+1档" },
    "exp": { "score": 9, "detail": "5年，达标" },
    "city": { "score": 10, "detail": "居住与意向城市一致" }
  },
  "rationale": "命中 8/10 必备技能、学历超标、补1个加分技能即可达90+",
  "graph_hints": ["为补齐 Kafka，建议先学其消息可靠性前置知识"]
}
```

- rationale 由后端按 breakdown 模板拼接，不让大模型逐条生成分数解释
- graph_hints 可选由 LLM 润色一句

---

## 懒计算 + 新鲜度

- 求职者打开推荐页 → 召回候选 → 逐对查 match_result
- 命中且未过期 → 返回缓存
- 缺失或 is_stale → 跑三层算法 → 写回 → 返回
- 简历/岗位技能变更 → 对应 match_result 标记 is_stale=true
- 企业端同理，方向反过来，读同一张表

---

## API 清单

### 1. GET `/api/match/jobs`

- 需要 USER 角色
- 求职者看推荐岗位（懒计算 + 缓存）
- 返回 `Result<{ jobs: [{ job_id, title, company, ..., score, match_detail }] }>`

### 2. GET `/api/match/candidates/{job_id}`

- 需要 COMPANY 角色
- 企业看某岗位的候选人推荐
- 返回 `Result<{ candidates: [{ resume_id, name, ..., score, match_detail }] }>`

### 3. POST `/api/match/apply`

- 求职者投递岗位
| 参数 | 类型 | 说明 |
|------|------|------|
| job_id | int | 投递的岗位 |
| resume_id | int | 使用的简历 |

- recommend_record.is_applied=true
- 给企业发 notification(type=APPLICATION)
- 返回 `Result[null]`

### 4. POST `/api/match/invite`

- 企业发起面试邀请
| 参数 | 类型 | 说明 |
|------|------|------|
| resume_id | int | 候选人简历 |
| job_id | int | 岗位 |

- recommend_record.is_invited=true
- 给求职者发 notification(type=INTERVIEW_INVITE)
- 返回 `Result[null]`

---

## 代码分层

| 层 | 文件 | 职责 |
|----|------|------|
| 路由 | `api/v1/match.py` | 四个端点 |
| 服务 | `services/match_service.py` | 匹配编排 + 懒计算 |
| 核心 | `core/matching/recall.py` | 召回层 |
| 核心 | `core/matching/scorer.py` | 维度打分 |
| 核心 | `core/matching/graph_boost.py` | 图谱增值 |
| 核心 | `core/matching/rationale_builder.py` | 模板拼接 rationale |
| 仓储 | `repositories/match_repository.py` | |
| 仓储 | `repositories/recommend_repository.py` | |

---

## 验收标准

- [ ] 求职者推荐 → 按 score 降序，每条带 match_detail
- [ ] 企业候选人推荐 → 同一对 match_result 复用，不算两次
- [ ] 投递 → notification 生成
- [ ] 邀请 → notification 生成
- [ ] match_detail 拆分到维度子分 + 命中/缺失列表
- [ ] 简历技能变更 → match_result is_stale → 下次请求重算
