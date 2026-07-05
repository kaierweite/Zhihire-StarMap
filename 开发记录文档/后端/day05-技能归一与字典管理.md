# Day 05 — 技能归一 + 字典管理

> **日期**：2026-07-10（周五）
> **阶段**：核心业务（一）
> **前置依赖**：Day 04（解析链路）

---

## 目标

完成技能归一入库流程（skill + synonym 双查兜底）、技能字典 CRUD。

---

## 任务清单

### 1. Skill 实体与 Mapper（1h）

- [x] `Skill` 实体：id, name, category, status(ACTIVE/CANDIDATE/MERGED), mergeTargetId
- [x] `SkillSynonym` 实体：id, skillId, synonym, mergeTargetId
- [x] `SkillRelation` 实体：id, skillIdA, skillIdB, relationType(PREREQUISITE/INCLUDES/SIMILAR/COMPLEMENTARY), weight
- [x] 各实体 Mapper extends BaseMapper

### 2. 技能归一入库 Service（2h）

- `SkillNormalizationService.normalizeSkill(raw, canonicalName, confidence)`：
  1. 按 canonicalName 唯一索引查 skill 表
  2. 若命中 → 返回 skillId
  3. 若未命中 → 查 skill_synonym 表（同义兜底）
  4. 若 synonym 命中 → 取 mergeTargetId 对应 ACTIVE 行的 skillId
  5. 若全未命中 → 创建 skill（status=CANDIDATE），返回新 skillId
- [x] `SkillNormalizationService.batchNormalize(skills)`：
  - [x] 批量归一，返回 List<{raw, skillId, confidence}>

### 3. 技能字典审核接口（1.5h）

- `module.admin.controller.AdminSkillController`：
  - `GET /api/admin/skill/list` — 技能列表（支持 status 筛选，分页）
  - `PUT /api/admin/skill/{id}` — 更新技能状态（CANDIDATE → ACTIVE）
  - `PUT /api/admin/skill/{id}/merge` — 合并技能（设 mergeTargetId，原技能 → MERGED）
  - `GET /api/admin/skill/synonym/list` — 同义词列表
  - `POST /api/admin/skill/synonym` — 添加同义词
  - `DELETE /api/admin/skill/synonym/{id}` — 删除同义词

### 4. 审核后触发图谱重建（0.5h）

- 技能状态变更后，调用 AI 服务 `POST /ai/graph/reload`
- AI 服务重建 networkx 常驻内存图

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/admin/entity/Skill.java` | 技能实体 |
| `module/admin/service/SkillNormalizationService.java` | 技能归一入库 |
| `module/admin/controller/AdminSkillController.java` | 字典审核接口 |
| `PUT /api/admin/skill/{id}` | 字典状态流转 |
| `POST /ai/graph/reload` | 审核后触发图谱重建 |

---

## 验收标准

- [x] canonicalName 查 skill 唯一索引命中 → 返回 skillId
- [x] 未命中时查 synonym 兜底 → 取 mergeTarget
- [x] 全未命中时创建 CANDIDATE 技能
- [x] 管理员可审核 CANDIDATE → ACTIVE
- [x] 合并操作设置 mergeTargetId + 原技能 → MERGED
- [x] 审核后触发 AI 图谱 reload
