# Day 02 — 数据库建表与种子数据

> **日期**：2026-07-07（周二）
> **阶段**：基础搭建
> **前置依赖**：Day 01（KingbaseES 连通）

---

## 目标

完成 27 张表建表脚本、索引、种子数据，数据库层就绪。

---

## 任务清单

### 1. 01_schema.sql — 27 张表 CREATE TABLE（3h）

按 `database/README.md` 定义，分三个依赖层次：

**第一批：基础表（无外键依赖）**
- [x] `user`（用户主表，角色 ADMIN/USER/COMPANY）
- `upload_file`（文件本体，单一事实源）
- `skill`（技能字典，status 三态 ACTIVE/CANDIDATE/MERGED + category）
- `occupation_role`（职业角色，原 role 重命名）
- `notification`（通知，is_read + type）

**第二批：关联表（依赖第一批）**
- [x] `user_profile`（求职者档案，current_city + profile_completeness）
- `company`（企业档案，audit_status + audit_reason）
- `resume`（简历，file_id FK → upload_file）
- `parse_task`（解析任务，file_id FK → upload_file）
- `job`（岗位，occupation_role_id + source MANUAL/UPLOAD + embedding_cache）
- `user_skill`（用户技能关联）
- `job_skill`（岗位技能关联，importance + required_level）
- `skill_relation`（技能边，relation_type 四类 + weight）
- `skill_synonym`（技能同义词）
- `occupation_role_skill`（角色技能关联，requirement_level）
- `match_result`（匹配结果，match_detail JSONB）
- `recommend_record`（推荐记录，is_clicked/is_applied/is_invited）
- `career_plan`（职业规划，结构化 JSON）
- `ability_graph`（图谱渲染缓存）
- `ai_chat_history`（对话历史）
- `login_log`（登录日志，append-only）
- `operation_log`（操作日志，append-only）

**第三批：面试模块表（ADR-0011）**
- [x] `interview_session`（面试会话）
- `interview_question`（面试问题，is_bank_visible）
- `interview_answer`（用户回答，ai_score + matched_points/missed_points）
- `interview_report`（面试报告，radar JSONB + feedback JSONB）
- `resume_optimization`（简历优化建议）

关键约束：
- [x] 所有业务表含 `created_at` / `updated_at` / `deleted_at`
- 日志类表仅 `created_at` + `deleted_at`
- `skill_relation` 自引用环外键用 `DEFERRABLE INITIALLY DEFERRED`
- 状态字段全 VARCHAR 大写语义枚举（ADR-0002）

### 2. 02_index.sql — 唯一索引与查询索引（1h）

- `skill.name` 唯一索引
- `skill_synonym.synonym` 唯一索引
- `user.username` 唯一索引
- `match_result (resume_id, job_id)` 联合唯一索引
- `resume.user_id`、`job.company_id`、`parse_task.file_id` 查询索引
- 面试模块：`interview_session.user_id`、`interview_question.session_id` 等

### 3. 03_seed.sql — 种子数据（2h）

- [x] admin 账号 1 条（username=admin, password=BCrypt）
- 80~120 条 ACTIVE 技能（覆盖演示简历/JD 技能，含 category 标注）
- ≥15 条 skill_synonym（SpringBoot/Spring-Boot → Spring Boot 等）
- 8~12 条 occupation_role（后端开发/测试/运维/前端/架构师/数据开发/产品经理/技术经理）
- 每个 occupation_role 对应 MUST/NICE/BONUS 技能（occupation_role_skill）
- ≥20 条 skill_relation 示例边（PREREQUISITE/SIMILAR/INCLUDES/COMPLEMENTARY 混合）

### 4. 执行建表脚本（0.5h）

- 连接 KingbaseES 执行三个 SQL 文件
- 验证 27 张表全部创建成功
- 验证种子数据行数正确

---

## 产出物

| 产出 | 说明 |
|------|------|
| `database/01_schema.sql` | 27 张表 DDL |
| `database/02_index.sql` | 唯一索引 + 查询索引 |
| `database/03_seed.sql` | 种子数据 |
| KingbaseES 数据库 | 27 表 + 种子数据就绪 |

---

## 验收标准

- [x] 27 张表全部创建成功
- [x] 所有唯一索引生效
- [x] seed 数据行数：skill ≥80, occupation_role ≥8, skill_synonym ≥15, skill_relation ≥20
- [x] BCrypt 密码可被 Spring Security 正确验证

