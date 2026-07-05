# Day 07 — 简历解析 + 用户技能入库

> **日期**：2026-07-12（周日）
> **阶段**：核心业务（二）
> **前置依赖**：Day 05（技能归一）+ Day 06（岗位模块）

---

## 目标

完成后端解析回调接口，实现简历解析结果 → 技能归一 → user_skill 入库全链路。

---

## 任务清单

### 1. 解析回调接口（1.5h）

- [x] `POST /api/parse/callback` — AI 服务解析完成后的回调接口
  - 接收：parseTaskId, rawData, parsedData(JSON), skills(List<{raw, canonicalName, confidence}>)
  - [x] 更新 parse_task.status = SUCCESS
  - 更新 resume.parsed_data = parsedData
  - 调 SkillNormalizationService.batchNormalize(skills) 归一入库
  - 写 user_skill（user_id + skill_id + confidence + rawText）
  - 计算 profileCompleteness（技能数/字段填充度）

### 2. 用户技能查询接口（1h）

- `GET /api/user/skills` — 当前用户的技能列表
  - 关联查 skill 表，返回 [{skillId, name, category, confidence, raw}]
- `DELETE /api/user/skills/{skillId}` — 删除用户技能

### 3. 简历解析状态接口完善（0.5h）

- `GET /api/resume/{id}/parse-status` — 简历解析状态
  - 返回 parse_task.status + 进度
  - FAILED/REJECTED 时返回错误原因

### 4. 用户档案完整度计算（1h）

- `UserProfileService.calculateCompleteness(userId)`：
  - 基于 user_skill 数量 + 基本信息填充度
  - 更新 user_profile.profile_completeness

---

## 产出物

| 产出 | 说明 |
|------|------|
| `POST /api/parse/callback` | 解析回调接口 |
| `GET /api/user/skills` | 用户技能列表 |
| `DELETE /api/user/skills/{skillId}` | 删除用户技能 |
| user_skill 入库 | 解析结果 → 归一 → 入库全链路 |

---

## 验收标准

- [x] AI 服务解析完成后回调后端，数据正确入库
- [x] 技能归一后 user_skill 正确关联
- [x] 用户技能列表返回 name + category + confidence
- [x] profileCompleteness 自动计算
