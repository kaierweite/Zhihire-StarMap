# Day 06 — 岗位模块

> **日期**：2026-07-11（周六）
> **阶段**：核心业务（一）
> **前置依赖**：Day 04（文件管理）+ Day 05（技能归一）

---

## 目标

完成岗位 CRUD（双模式：手动填写 / JD 上传）、岗位技能关联。

---

## 任务清单

### 1. Job 实体与 Mapper（0.5h）

- [x] `Job` 实体：id, companyId, title, description, city, salary, education, experience, status(OPEN/CLOSED/DRAFT), source(MANUAL/UPLOAD), occupationRoleId, embeddingCache(JSONB)
- [x] `JobSkill` 实体：id, jobId, skillId, importance(FLOAT 1~5), requiredLevel(MUST/NICE/BONUS)
- [x] `OccupationRole` 实体：id, name, description

### 2. 岗位手动填写接口（1.5h）

- [x] `POST /api/job/create`（source=MANUAL）
  - 接收岗位基本信息 + 技能列表（从字典下拉，必为 ACTIVE）
  - 校验所有 skillId 对应的技能状态为 ACTIVE
  - 写入 job + job_skill
  - 根据 JD 内容匹配 occupation_role（名称匹配兜底）
- `PUT /api/job/{id}` — 更新岗位
- `PUT /api/job/{id}/status` — 切换状态（OPEN/CLOSED/DRAFT）
- `GET /api/job/list` — 岗位列表（企业维度，分页）

### 3. 岗位 JD 上传接口（1.5h）

- `POST /api/job/create`（source=UPLOAD）
  - 接收 JD 文件（PDF/DOC/DOCX）
  - 存储文件（复用 SystemFileService）
  - 创建 parse_task
  - 异步调 AI 服务 `POST /ai/parse/job`
  - AI 返回：技能归一名列表 + occupation_role_name + 结构化需求
  - [x] 后端技能归一入库 + job_skill 关联
  - 绑定 job.occupation_role_id

### 4. 岗位对外查询接口（0.5h）

- `GET /api/job/public/list` — 对外岗位列表（仅 status=OPEN 且 company.audit_status=VERIFIED）
- `GET /api/job/public/{id}` — 岗位详情

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/job/` | 岗位 CRUD + 双模式 |
| `POST /api/job/create` | 手动填写 / JD 上传双模式 |
| `PUT /api/job/{id}/status` | 岗位状态切换 |
| `GET /api/job/public/list` | 对外岗位列表（审核过滤） |

---

## 验收标准

- [x] 手动填写 JD：技能从字典下拉（ACTIVE），直接写 job_skill
- [x] JD 上传：异步解析 → 技能归一入库 → job_skill 关联
- [x] occupation_role 匹配：JD 解析输出 role_name → 查表绑定
- [x] 未审核企业（audit_status != VERIFIED）岗位不对外返回
