# Day 02 — User 用户档案模块

> **前置依赖**：day01 auth
> **前端对应**：UserProfile.vue / UserDashboard.vue

---

## 目标

求职者个人档案的读取与编辑，包括基本信息、教育经历、工作经历、项目经历、技能标签、求职意向。
前端 UserProfile.vue 当前用模拟数据展示，需替换为真实接口。

---

## 涉及数据表

- `user` — 用户主表
- `user_profile` — 档案扩展表（city, target_city, graduation_year, job_status, intention 等）
- `user_skill` — 用户技能关联表（user_id, skill_id, level）
- `user_education` — 教育经历
- `user_experience` — 工作/项目经历

---

## API 清单

### 1. GET `/api/user/profile`

- 需要 USER 角色
- 返回完整档案 JSON `Result<UserProfileDTO>`
- 包含基本信息 + 教育经历数组 + 工作经历数组 + 技能数组 + 意向

### 2. PUT `/api/user/profile`

- 需要 USER 角色
- 接收档案更新数据，逐 section 更新

| 参数 | 类型 | 说明 |
|------|------|------|
| name | string | 姓名 |
| gender | string | 性别 |
| city | string | 当前城市 |
| target_cities | string | 意向城市（逗号分隔） |
| job_status | string | 求职状态 |
| education | array | 教育经历 |
| work | array | 工作经历 |
| skills | array | 技能名列表（需归一到 skill_id） |
| intention | object | 意向（薪资/工作类型/行业） |

- 技能写入 `user_skill`，通过 skill_id 关联
- 返回更新后 `Result<UserProfileDTO>`

---

## 代码分层

| 层 | 文件 |
|----|------|
| 路由 | `api/v1/user.py` |
| 服务 | `services/user_service.py` |
| 仓储 | `repositories/user_repository.py` |
| 仓储 | `repositories/user_skill_repository.py` |
| 模型 | `models/entities/user.py` |
| 模型 | `models/schemas/user.py` |

---

## 验收标准

- [ ] 登录后 GET 返回个人档案
- [ ] PUT 修改后 GET 能看到变更
- [ ] 技能写入 user_skill 并关联 skill_id
- [ ] profile_completeness 字段自动计算
