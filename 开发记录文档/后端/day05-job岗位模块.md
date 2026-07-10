# Day 05 — Job 岗位模块

> **前置依赖**：day01 auth + day00 LLM 客户端
> **前端对应**：JobManage.vue / JobPublish.vue / JobRecommend.vue / JobSearch.vue / JobDetail.vue / SmartScreening.vue
> **核心 ADR**：V4 Q12（岗位双模式）

---

## 目标

企业发布岗位（手动填写 / JD 文件上传双模式），求职者搜索和查看岗位，JD 文件上传走 AI 解析。

---

## 涉及数据表

- `job` — 岗位主表（company_id, title, city, edu, exp, salary_min, salary_max, type, description, source, status, views, created_at）
- `job_skill` — 岗位技能关联（job_id, skill_id, importance, requirement_level）
- `company` — 企业表（审核状态影响岗位对外可见性）
- `occupation_role` — 职业角色

---

## 岗位双模式

- **手动填写**（source=MANUAL）：企业表单直接填 job + job_skill，技能从字典下拉（必为 ACTIVE）
- **JD 上传**（source=UPLOAD）：JD 文件走 AI 解析，同简历解析链路，结果回填 job + job_skill

---

## API 清单

### 1. POST `/api/job`

- 需要 COMPANY 角色
- 手动发布岗位
| 参数 | 类型 | 说明 |
|------|------|------|
| title | string | 岗位名称 |
| city | string | 工作城市 |
| edu | string | 学历要求 |
| exp | string | 经验要求 |
| salary_min/max | int | 薪资范围 |
| type | string | 全职/兼职/实习 |
| description | string | 岗位描述 |
| skills | array | 技能列表 [{ skill_id, importance, requirement_level }] |
| benefits | array | 福利标签 |

- 企业未审核 → 岗位 status=DRAFT
- 已审核 → status=OPEN
- 返回 `Result<{ job_id }>`

### 2. POST `/api/job/upload-parse`

- 需要 COMPANY 角色
- multipart 上传 JD 文件
- 调 DeepSeek 解析 JD → 结构化回填表单字段（前端可直接填充）
- 返回 `Result<{ parsed_job_data }>`（不落库，仅给前端填表）

### 3. PUT `/api/job/{job_id}`

- 编辑岗位信息 + 技能

### 4. PUT `/api/job/{job_id}/status`

- status 切换：DRAFT / OPEN / CLOSED / PAUSED

### 5. GET `/api/job/company/list`

- 需要 COMPANY 角色
- 企业自己的岗位列表（含未发布/草稿）+ 分页
- 返回 `Result<PageData<JobVO>>`

### 6. GET `/api/job/search`

- 公开（需要登录）
- 求职者搜索岗位，多维筛选
| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 关键词 |
| city | string | 城市筛选 |
| edu | string | 学历筛选 |
| type | string | 工作类型 |
| company_type | string | 企业类型 |
| salary_min/max | int | 薪资区间 |
| page/size | int | 分页 |

- 只返回 status=OPEN + 企业 audit_status=VERIFIED 的岗位
- 返回 `Result<PageData<JobVO>>`

### 7. GET `/api/job/recommend`

- 需要 USER 角色
- AI 推荐岗位（匹配分排序，见 day06）
- 返回 `Result<{ jobs: [{ ...job, match_score, match_detail }] }>`

### 8. GET `/api/job/{job_id}`

- 岗位详情 + 技能要求 + 企业信息
- views +1
- 返回 `Result<JobDetailVO>`

---

## 代码分层

| 层 | 文件 |
|----|------|
| 路由 | `api/v1/job.py` |
| 服务 | `services/job_service.py` |
| 仓储 | `repositories/job_repository.py` |
| 仓储 | `repositories/job_skill_repository.py` |

---

## 验收标准

- [ ] 企业手动发布岗位 → 草稿状态（未审核）
- [ ] JD 上传 → AI 解析回填表单字段
- [ ] 求职者搜索只看到 OPEN + VERIFIED 的岗位
- [ ] 筛选维度全部生效
- [ ] 岗位详情 views 递增
