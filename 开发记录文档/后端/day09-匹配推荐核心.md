# Day 09 — 匹配推荐核心

> **日期**：2026-07-14（周二）
> **阶段**：核心业务（三）
> **前置依赖**：Day 07（用户技能）+ Day 06（岗位技能）

---

## 目标

完成后端匹配推荐核心逻辑：候选召回 + 调 AI 评分 + match_result 懒计算 + 新鲜度缓存。

---

## 任务清单

### 1. MatchResult 实体（0.5h）

- [x] `MatchResult` 实体：id, resumeId, jobId, score, matchDetail(JSONB), createdAt, updatedAt
- [x] `match_detail` 固定结构：
  ```json
  {
    "score": 87,
    "breakdown": {
      "skill": {"score": 85, "hit": [...], "miss": [...]},
      "edu": {"score": 90, "detail": "..."},
      "exp": {"score": 88, "detail": "..."},
      "city": {"score": 100, "detail": "..."}
    },
    "rationale": "模板拼接文本",
    "graph_hints": ["建议学习..."]
  }
  ```

### 2. 候选召回 Service（1.5h）

- [x] `RecommendService`：
  - [x] 候选岗位召回（求职者视角）：
    - [x] SQL 查当前用户 user_skill 的 skillId 列表
    - 查 job_skill 关联的 job 列表
    - skill_synonym 同义扩展
    - 候选集硬封顶 ≤50
  - 候选人才召回（企业视角）：
    - [x] SQL 查岗位 job_skill 的 skillId 列表
    - 查 user_skill 关联的 user 列表
    - 候选集 ≤50

### 3. 懒计算 + 新鲜度缓存（1.5h）

- `RecommendService.getOrCreateMatchResult(resumeId, jobId)`：
  1. 查 match_result（resume_id + job_id）
  2. 若命中且 updated_at > max(resume_skill_updated_at, job_skill_updated_at) → 直接返回
  3. 若未命中或过期 → 调 AI 服务 `/ai/recommend/match`
  4. AI 返回 match_detail → 写入 match_result
  5. 返回结果

### 4. 推荐列表接口（1.5h）

- [x] `GET /api/recommend/jobs` — 求职者岗位推荐（分页）
  - 查当前用户所有 match_result → 排序 → 分页返回
  - 翻页不重调 AI（基于已缓存 match_result）
- `GET /api/recommend/talents` — 企业人才推荐（分页）
  - 查该岗位所有 match_result → 排序 → 分页返回
- `GET /api/recommend/job/{jobId}/detail` — 某岗位匹配详情
  - 触发懒计算，返回 match_detail

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/match/entity/MatchResult.java` | 匹配结果实体 |
| `module/match/service/RecommendService.java` | 推荐核心逻辑 |
| `module/match/controller/RecommendController.java` | 推荐接口 |
| `GET /api/recommend/jobs` | 求职者岗位推荐 |
| `GET /api/recommend/talents` | 企业人才推荐 |

---

## 验收标准

- [x] 候选召回 ≤50，同义扩展生效
- [x] 懒计算：首次请求调 AI，二次请求直接返回缓存
- [x] 新鲜度：技能变更后自动重新计算
- [x] 双向共用 match_result，按方向读视图
- [x] 分页返回 {records, total, page, size}
