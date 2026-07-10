# 智聘星图 后端 API 总览 — 前端对接手册

## 基础信息

- 基础路径：`/api`
- 响应封装：所有接口返回 `Result<T>`：

```json
{ "code": 200, "message": "success", "data": { ... } }
```

- 认证方式：JWT Bearer Token（`Authorization: Bearer <token>`）
- 角色体系：`USER`（求职者）/ `COMPANY`（企业）/ `ADMIN`（管理员）

---

## 模块清单（共 11 个路由文件）

---

### 一、认证 /api/auth

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| /api/auth/register | POST | 无 | 注册（USER 或 COMPANY） |
| /api/auth/login | POST | 无 | 登录，返回 JWT |
| /api/auth/me | GET | 任意 | 获取当前用户信息 |

**注册（POST /api/auth/register）**
```json
{
  "username": "zhangsan",
  "password": "123456",
  "role": "USER",
  "email": "zs@example.com",
  "phone": "13800138000",
  "company_name": null,
  "contact_email": null,
  "contact_phone": null
}
```
- `role` 仅允许 `USER` 或 `COMPANY`
- 企业注册时需传 `company_name`
- 注册后 Company 的 audit_status 为 UNVERIFIED，需管理员审核后才能发岗位

**登录（POST /api/auth/login）**
```json
// 请求
{ "username": "zhangsan", "password": "123456" }
// 响应 data
{ "token": "eyJ...", "role": "USER", "username": "zhangsan" }
```
- `token` 存 localStorage，后续所有请求带 `Authorization: Bearer <token>`

**当前用户（GET /api/auth/me）**
```json
// 响应 data
{ "id": 1, "username": "zhangsan", "role": "USER", "email": "zs@example.com", "phone": "13800138000", "status": "NORMAL", "created_at": "2026-07-07T10:00:00" }
```

---

### 二、用户档案 /api/user

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| /api/user/profile | GET | USER | 获取个人完整档案 |
| /api/user/profile | PUT | USER | 更新个人档案 |

**GET /api/user/profile 响应字段**
```
id, username, avatar_url, real_name, gender, birth_date,
phone, email, education, school, major, work_years,
current_city, expected_city, expected_position, expected_worktype,
expected_industry, expected_salary_min, expected_salary_max,
bio, profile_completeness, created_at

--- 子列表 ---
skills: [{ skill_id, name, category, proficiency_level }]
work_experiences: [{ title, company, period, description }]
project_experiences: [{ name, description }]
languages: [{ name, level }]
certificates: [{ name }]
```

**PUT /api/user/profile 更新**
- 所有字段可选，只传要修改的字段
- 多值列表全量替换（前端传完整数组，后端先删后插）
- `skills` 传技能名列表 `["Vue 3", "Python"]`，服务端自动归一化到 skill_id
- `expected_salary_min/max` 以 K/月为单位

---

### 三、简历 /api/resume

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| /api/resume/upload | POST | USER | 上传简历文件 |
| /api/resume | GET | USER | 简历列表（分页） |
| /api/resume/{id} | GET | USER | 简历详情 |
| /api/resume/{id} | PUT | USER | 编辑简历内容 |
| /api/resume/{id} | DELETE | USER | 删除简历 |
| /api/resume/optimize | POST | USER | AI 优化简历 |

**上传（POST /api/resume/upload）**
- `multipart/form-data`，传 `file` 和可选 `title`
- 支持 PDF / DOC / DOCX
- 后台异步解析，返回 `{ resume_id, file_id, task_id, title }`

**查询解析状态（GET /api/parse/task/{task_id}）**
- 上传后轮询此端点，`status` 为 `SUCCESS` 或 `FAILED`
- 成功后 `result` 包含解析出的结构化 JSON

**AI 优化（POST /api/resume/optimize）**
```json
{ "resume_id": 3, "job_description": "高级前端..." }
// 响应 data
{ "resume_id": 3, "suggestions": [{ "section": "技能", "current": "Vue 2", "suggestion": "...", "relates_to_skill": "Vue 3" }] }
```

---

### 四、技能字典 /api/skills

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| /api/skills | GET | 无 | 模糊搜索技能 |

**GET /api/skills?search=Vue&limit=20**
```json
// 响应 data
[{ "id": 12, "name": "Vue 3", "category": "前端" }, ...]
```
- 用于岗位发布/简历编辑时的技能下拉选择器
- `search` 为空时返回全量

---

### 五、企业 /api/company

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| /api/company/me | GET | COMPANY | 当前企业信息 |

**GET /api/company/me 响应字段**
```
id, company_name, industry, scale, description, website,
logo_url, address, contact_name, contact_phone, contact_email,
audit_status
```

- `audit_status`: `UNVERIFIED` / `PENDING` / `VERIFIED` / `REJECTED`
- 仅 `VERIFIED` 状态才能发布岗位

---

### 六、岗位 /api/job

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| POST /api/job | POST | COMPANY | 创建岗位 |
| GET /api/job | GET | 无 | 搜索岗位（分页） |
| GET /api/job/{id} | GET | 无 | 岗位详情 |
| PUT /api/job/{id} | PUT | COMPANY | 更新岗位 |
| DELETE /api/job/{id} | DELETE | COMPANY | 删除岗位 |
| POST /api/job/{id}/skills | POST | COMPANY | 添加技能要求 |
| GET /api/job/{id}/skills | GET | 无 | 岗位技能列表 |
| DELETE /api/job/{id}/skills/{skill_id} | DELETE | COMPANY | 移除技能要求 |
| POST /api/job/{id}/apply | POST | USER | 投递简历 |

**创建岗位（POST /api/job）**
```json
{
  "title": "高级前端工程师",
  "city": "北京",
  "education_requirement": "本科",
  "experience_min": 3,
  "salary_min": 20000,
  "salary_max": 35000,
  "job_type": "FULL_TIME",
  "description": "...",
  "occupation_role_id": 5,
  "benefits": ["五险一金", "弹性工作"]
}
```

**搜索岗位（GET /api/job）**
```
参数：keyword, city, education_requirement, experience_min,
      salary_min, salary_max, job_type, company_id, status,
      page, size
```
- 返回 `PageResult`（records + total + page + size）
- 默认只查 `status=OPEN` 的岗位
- `GET /api/job?keyword=前端&city=北京&page=1&size=20`

**岗位详情（GET /api/job/{id}）**
- 无需登录，自动增加浏览次数
- 返回含技能列表 `skills: [{ id, skill_id, skill_name, skill_category, importance, required_level }]`

**岗位技能管理**
- `required_level`: `MUST` / `NICE` / `BONUS`
- `importance`: 1~5

---

### 七、匹配推荐 /api/match （Day06 核心）

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| GET /api/match/jobs | GET | USER | 求职者推荐岗位 |
| GET /api/match/candidates/{job_id} | GET | COMPANY | 企业候选人推荐 |
| POST /api/match/apply | POST | USER | 投递岗位 |
| POST /api/match/invite | POST | COMPANY | 邀请面试 |

**求职端（GET /api/match/jobs）**
- 无参数，后端自动召回+打分+缓存
- 按 `score` 降序，每条含完整 `match_detail`（见下）

**企业端（GET /api/match/candidates/{job_id}）**
- 岗位需属于当前企业
- 与求职端共享 match_result 表，不重复计算

**match_detail 结构**
```json
{
  "score": 87.53,
  "breakdown": {
    "skill": { "score": 8.7, "hit": ["12","35"], "miss": ["78"], "detail": "必备2/3" },
    "edu": { "score": 12, "detail": "硕士，超标+1档" },
    "exp": { "score": 10, "detail": "5年，达标" },
    "city": { "score": 10, "detail": "居住与岗位城市一致" }
  },
  "rationale": "必备2/3、硕士，超标+1档、...",
  "graph_hints": ["您已掌握React（与Vue_3相似），可快速上手"]
}
```
- `hit`/`miss` 目前只返回 skill_id（string），**不返回 skill_name**，前端如需展示名称需额外调 `/api/skills`
- 无分页参数，目前硬限 50 条

**投递（POST /api/match/apply）**
```json
{ "job_id": 12, "resume_id": 3 }
```
- 重复投递返回 409

**邀请（POST /api/match/invite）**
```json
{ "resume_id": 3, "job_id": 12 }
```

---

### 八、能力图谱 /api/graph

| 端点 | 方法 | 角色 | 用途 |
|------|------|------|------|
| GET /api/graph/user | GET | USER | 个人能力图谱 |
| GET /api/graph/job/{job_id} | GET | USER | 岗位技能图谱 |
| POST /api/graph/reload | POST | ADMIN | 管理员重建图谱 |
| GET /api/graph/roles | GET | USER | 职业角色列表 |

**图谱响应（GET /api/graph/user）**
```json
{
  "nodes": [{ "id": "12", "name": "Vue 3", "category": "前端", "level": 4.0, "level_label": "advanced", "symbolSize": 30, "itemStyle": null }],
  "edges": [{ "source": "12", "target": "35", "relation_type": "PREREQUISITE", "weight": 0.5, "lineStyle": {} }],
  "state": "ready",
  "categories": [{ "name": "前端", "color": "#... " }],
  "gap_skills": [{ "skill_name": "Kafka", "requirement_level": "MUST" }]
}
```
- `GET /api/graph/user?role_id=5` 附带技能差距分析
- `gap_skills` 按 MUST→NICE→BONUS 排序
- 图谱由 networkx 常驻内存构建，通过 ECharts 关系图渲染

**职业角色（GET /api/graph/roles）**
```json
[{ "id": 1, "name": "前端工程师", "category": "前端", "description": "..." }]
```
- 用于前端「目标职业」下拉选择器

---

### 九、投递冗余说明

目前有两个投递入口，后端共用同一套逻辑：

| 路径 | 所属模块 |
|------|----------|
| POST /api/job/{id}/apply | job 模块（早期） |
| POST /api/match/apply | match 模块（Day06，推荐模块常规走法） |

两者效果完全一致，前端推荐页走 `POST /api/match/apply`，岗位详情页也可以走 `POST /api/job/{id}/apply`。

---

## 前端对接路线图

### 第一阶段：认证 + 用户（第 1 天）
1. `POST /api/auth/register` + `POST /api/auth/login`
2. 存 token，后续请求带 Authorization header
3. `GET /api/user/profile` + `PUT /api/user/profile`（编辑档案）
4. `GET /api/skills?search=`（技能下拉）

### 第二阶段：简历（第 2 天）
1. `POST /api/resume/upload` + `GET /api/parse/task/{id}`（上传+轮询解析）
2. `GET /api/resume` + `GET /api/resume/{id}`（列表+详情）

### 第三阶段：岗位（第 3 天）
1. `GET /api/job` + `GET /api/job/{id}`（搜索+详情浏览）
2. 企业端：岗位 CRUD + 技能管理

### 第四阶段：匹配推荐 + 图谱（第 4 天）
1. `GET /api/match/jobs`（推荐页，带 match_detail 展示）
2. `POST /api/match/apply`（投递）
3. `GET /api/graph/user` + `GET /api/graph/roles`（能力图谱）
4. 企业端：`GET /api/match/candidates/{id}` + `POST /api/match/invite`

---

## 错误处理

```
200 → 成功，check data
4xx → 业务错误，check code + message
500 → 服务端异常（兜底）
```

通用错误码：
| code | 含义 |
|------|------|
| 200 | 成功 |
| 401 | 未登录或 token 过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 冲突（如重复投递） |
| 422 | 请求参数校验失败 |
