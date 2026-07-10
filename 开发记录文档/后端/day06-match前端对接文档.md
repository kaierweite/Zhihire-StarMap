# Match 匹配推荐模块 — 前端对接文档

## 4 个 API 端点

所有端点统一前缀 `/api/match`，响应封装为 `Result<T>`：

```json
{ "code": 200, "message": "success", "data": { ... } }
```

---

### 1. GET /api/match/jobs

> 求职者看推荐岗位（懒计算 + 新鲜度缓存）

**角色**：`USER`

**请求**：无参数

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "jobs": [
      {
        "job_id": 12,
        "resume_id": 3,
        "title": "高级前端工程师",
        "company_name": "某科技公司",
        "score": 87.53,
        "match_detail": {
          "score": 87.53,
          "breakdown": {
            "skill": { "score": 8.7, "hit": ["Vue_3","TypeScript"], "miss": ["Kafka"], "detail": "必备2/3、技能分8.7" },
            "edu": { "score": 12, "detail": "硕士，超标+1档" },
            "exp": { "score": 10, "detail": "5年，达标" },
            "city": { "score": 10, "detail": "居住与岗位城市一致" }
          },
          "rationale": "必备2/3、硕士，超标+1档、5年，达标、居住与岗位城市一致、补1个缺口技能即可提升匹配度",
          "graph_hints": [
            "您已掌握React（与Vue_3相似），可快速上手",
            "为补齐Kafka，建议先学其消息可靠性前置知识"
          ]
        }
      }
    ]
  }
}
```

**行为说明**：
- 首次打开或简历/岗位技能变更后，后端自动跑三层算法（召回→打分→图谱增值）并缓存
- 缓存命中且 `is_stale=false` 直接返回，不做重复计算
- 返回按 `score` 降序排列
- 如果没有技能交集，返回空数组

---

### 2. GET /api/match/candidates/{job_id}

> 企业看某岗位的候选人推荐

**角色**：`COMPANY`

**路径参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| job_id | int | 岗位ID |

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "candidates": [
      {
        "job_id": 12,
        "resume_id": 3,
        "user_id": 7,
        "name": "张三",
        "score": 87.53,
        "match_detail": { "score": 87.53, "breakdown": {...}, "rationale": "...", "graph_hints": [...] }
      }
    ]
  }
}
```

**行为说明**：
- 与求职端共享同一张 `match_result` 表，同一对 (resume_id, job_id) 不重复计算
- 岗位必须属于当前企业，否则返回 404
- `name` 取自 `user.real_name` 或 `user.username`

---

### 3. POST /api/match/apply

> 求职者投递岗位

**角色**：`USER`

**请求体**：
```json
{
  "job_id": 12,
  "resume_id": 3
}
```

**响应**：
```json
{
  "code": 200,
  "message": "投递成功",
  "data": {
    "application_id": 45,
    "status": "APPLIED"
  }
}
```

**行为说明**：
- 重复投递同一岗位返回 `409`（与现有 job 模块行为一致）
- 岗位必须为 OPEN 状态，否则返回 404
- 成功后自动标记对应的 `recommend_record.is_applied = true`

---

### 4. POST /api/match/invite

> 企业邀请候选人面试

**角色**：`COMPANY`

**请求体**：
```json
{
  "resume_id": 3,
  "job_id": 12
}
```

**响应**：
```json
{
  "code": 200,
  "message": "邀请已发送",
  "data": {
    "record_id": 78,
    "user_id": 7,
    "status": "invited"
  }
}
```

**行为说明**：
- 岗位必须属于当前企业，否则返回 404
- 自动创建/更新 `recommend_record`，`recommend_type=TALENT`，标记 `is_invited=true`
- 同一个候选人可被邀请到不同岗位，无重复限制

---

## match_detail JSONB 结构详解

```json
{
  "score": 87.53,
  "breakdown": {
    "skill": {
      "score": 8.7,
      "hit": ["12", "35"],
      "miss": ["78"],
      "detail": "必备2/3、技能分8.7"
    },
    "edu": {
      "score": 12,
      "detail": "硕士，超标+1档"
    },
    "exp": {
      "score": 10,
      "detail": "5年，达标"
    },
    "city": {
      "score": 10,
      "detail": "居住与岗位城市一致"
    }
  },
  "rationale": "必备2/3、硕士，超标+1档、5年，居住与岗位城市一致、补1个缺口技能即可提升匹配度。您已掌握React（与Vue_3相似），可快速上手",
  "graph_hints": ["您已掌握React（与Vue_3相似），可快速上手"]
}
```

**字段说明**：
| 路径 | 类型 | 说明 |
|------|------|------|
| score | float | 总分 0~100 |
| breakdown.skill.score | float | 技能维度分 0~10 |
| breakdown.skill.hit | string[] | 命中的技能 ID 列表 |
| breakdown.skill.miss | string[] | 缺失的技能 ID 列表 |
| breakdown.edu.score | float | 学历维度分 0~12（超标可超 10） |
| breakdown.exp.score | float | 经验维度分 0~10 |
| breakdown.city.score | float | 城市维度分 0~10 |
| rationale | string | 可解释文本，由后端按 breakdow 模板拼接 |
| graph_hints | string[] | 图谱增值提示列表 |

**维度权重**（可配）：
| 维度 | 默认权重 |
|------|----------|
| skill | 0.40 |
| edu | 0.20 |
| exp | 0.20 |
| city | 0.20 |

---

## 新鲜度机制（前端无需关心，但要了解行为）

1. 简历技能变更 → 后端调用 `match_repository.mark_stale(resume_id=X)` → 标记该简历所有缓存为 `is_stale=true`
2. 岗位技能变更 → 后端调用 `match_repository.mark_stale(job_id=Y)` → 标记该岗位的所有缓存为 `is_stale=true`
3. 下次请求 `GET /api/match/jobs` 或 `GET /api/match/candidates/{id}` 时，`is_stale=true` 的条目触发重算
4. 这一层对前端完全透明，响应结构一致

---

## 错误码

| HTTP | code | message | 原因 |
|------|------|---------|------|
| 401 | 401 | 未登录或 token 过期 | 需要重新登录 |
| 403 | 403 | 企业不存在/未通过审核 | 企业端操作前检查 |
| 404 | 404 | 岗位不存在 | job_id 无效或已软删 |
| 404 | 404 | 简历不存在 | resume_id 无效 |
| 409 | 409 | 已投递过该岗位 | 重复投递被拦截 |

---

## 前端推荐页数据流转示意

```
用户打开「职位推荐」页面
       ↓
GET /api/match/jobs
       ↓
后端：召回候选岗位 → 逐对检查 match_result 缓存
  ├─ 命中且未过期 → 直接返回
  └─ 缺失或过期 → 三层算法计算 → 写缓存 → 返回
       ↓
前端：渲染 jobs 列表，每个卡片展示：
  - 标题、公司名、总分 score
  - match_detail.rationale 作为可解释文字
  - breakdown 四维度子分用于蛛网图/进度条
       ↓
用户点击「投递」按钮
       ↓
POST /api/match/apply
```
