# 智聘星图数据库目录

> 数据库：KingbaseES V8 R6（PostgreSQL 兼容模式）
> 口径以 V4 决策 + ADR-0008 D6 + ADR-0011（面试模块）为准。

## 建表文件（待产出）

本目录按 ADR-0008 D5 拆三个文件按依赖分层落 27 表（22 基础表 + 5 面试模块表）：

- `01_schema.sql` — 27 张表 `CREATE TABLE`。
  - 状态字段全 `VARCHAR` 大写语义枚举（ADR-0002）：`NORMAL/DISABLED/BANNED`、
    `OPEN/CLOSED/DRAFT`、`ACTIVE/CANDIDATE/MERGED`、`MUST/NICE/BONUS`、
    `UNVERIFIED/PENDING/VERIFIED/REJECTED`、`MANUAL/UPLOAD`、
    `WAITING/PARSING/SUCCESS/FAILED/REJECTED`、
    `PENDING/IN_PROGRESS/COMPLETED/ABORTED`（面试会话）、
    `TECHNICAL/BEHAVIORAL/SITUATIONAL/RESUME_BASED`（面试题型）等
  - 所有业务表含 `created_at` / `updated_at` / `deleted_at` 三时间字段
    （日志类 append-only 表仅 `created_at` + `deleted_at`）
  - `skill_relation` 自引用环外键用 `DEFERRABLE INITIALLY DEFERRED` 或后置 `ALTER`
- `02_index.sql` — 唯一索引与查询索引
  - `skill.name` 唯一索引（归一查表兜底）
  - `user.username` 唯一索引
  - `resume.user_id`、`job.company_id`、`match_result.{resume_id,job_id}` 等
  - `match_result (resume_id, job_id)` 联合唯一索引（懒计算兜底）
  - `interview_session.user_id`、`interview_question.session_id`、
    `interview_answer.question_id`、`interview_report.session_id`、
    `resume_optimization.resume_id`
- `03_seed.sql` — 种子数据
  - `occupation_role` 8~12 条职业角色（后端开发、测试、运维、前端、架构师、
    数据开发、产品经理、技术经理等），对应 MUST/NICE/BONUS 技能
  - admin 账号一条
  - **80~120 条 ACTIVE 技能**（覆盖演示简历/JD 技能）+ `category` 字段标注
  - `skill_synonym` 同义表 ≥15 条（SpringBoot/Spring-Boot → Spring Boot 等）
  - `skill_relation` 示例边 ≥10 条（PREREQUISITE / SIMILAR / INCLUDES / COMPLEMENTARY）

## 27 表清单（V4 收口 + ADR-0011 面试模块）

> V4 Q11：`role` → `occupation_role`（职业角色），`role_skill` → `occupation_role_skill`。
> 重命名不增表数，仍为 22 基础表。用户角色保持 `user.role` 字段不变（枚举常量）。
> ADR-0011：新增 5 张面试模块表（#23~#27），22 → 27 表。

| # | 表 | 说明 | 三时间字段 | V4 变更 |
|---|----|------|-----------|---------|
| 1 | `user` | 用户主表（角色大写枚举） | 全 | — |
| 2 | `user_profile` | 求职者档案 | 全 | + `current_city`、+ `profile_completeness INT(0~100)` |
| 3 | `company` | 企业档案 | 全 | + `audit_status`（UNVERIFIED/PENDING/VERIFIED/REJECTED）、+ `audit_reason` |
| 4 | `resume` | 简历实体（`file_id` 引用 `upload_file`） | 全 | + `embedding_cache JSONB` |
| 5 | `job` | 岗位 | 全 | + `occupation_role_id`、+ `source`（MANUAL/UPLOAD）、+ `embedding_cache JSONB` |
| 6 | `skill` | 技能字典（`status` 三态 + `merge_target_id`） | 全 | + `category`（后端/前端/测试/运维/数据/通用） |
| 7 | `user_skill` | 用户与技能关联 | 全 | — |
| 8 | `job_skill` | 岗位与技能关联（`importance` FLOAT(1~5)、`required_level` MUST/NICE/BONUS） | 全 | `importance` 量纲钉死 |
| 9 | `match_result` | 匹配结果（双向共用；删 `reason` 并入 `match_detail.rationale`） | 全 | 懒计算 + 新鲜度缓存口径 |
| 10 | `recommend_record` | 推荐记录（`is_clicked`、`is_applied`） | 全 | + `is_invited BOOLEAN` |
| 11 | `career_plan` | 职业规划 | 全 | 字段契约钉死 `{target_role, gap_skills[], learning_path[], graph_hints, rationale}` + LLM 润色句列 |
| 12 | `login_log` | 登录日志 | 仅 `created_at`+`deleted_at` | — |
| 13 | `operation_log` | 操作日志 | 仅 `created_at`+`deleted_at` | AOP `@OperationLog` 落库 |
| 14 | `notification` | 通知 | 仅 `created_at`+`deleted_at` | + `is_read BOOLEAN`、+ `type`（APPLICATION/INTERVIEW_INVITE/SYSTEM） |
| 15 | `upload_file` | 文件本体（**单一事实源**） | 仅 `created_at`+`deleted_at` | — |
| 16 | `parse_task` | 解析任务（`file_id` 引用 `upload_file`） | 全 | `status` + `REJECTED` 枚举 |
| 17 | `ability_graph` | 图谱渲染缓存（**非图谱本体**，权威在 AI 内存） | 全 | — |
| 18 | `ai_chat_history` | 规划/解析对话历史 | 仅 `created_at`+`deleted_at` | — |
| 19 | `skill_relation` | 技能边表（`relation_type` 大写四类 + `weight`） | 全 | SIMILAR/PREREQUISITE 边预置口径 |
| 20 | `occupation_role` | 职业角色（V4 Q11 从 `role` 重命名，区别于用户角色） | 全 | 重命名 |
| 21 | `occupation_role_skill` | 角色技能关联（`requirement_level` 大写 `MUST/NICE/BONUS`） | 全 | 重命名（原 `role_skill`） |
| 22 | `skill_synonym` | 技能同义词（支撑三态合并） | 全 | — |
| 23 | `interview_session` | 面试会话（`status`：PENDING/IN_PROGRESS/COMPLETED/ABORTED） | 全 | ADR-0011 新增 |
| 24 | `interview_question` | 面试问题（`question_type`、`expected_points JSONB`、`is_bank_visible`） | 全 | ADR-0011 新增 |
| 25 | `interview_answer` | 用户回答（`ai_score`、`ai_feedback`、`matched_points`、`missed_points`） | 全 | ADR-0011 新增 |
| 26 | `interview_report` | 面试报告（`overall_score`、`radar JSONB`、`feedback JSONB`） | 全 | ADR-0011 新增 |
| 27 | `resume_optimization` | 简历优化建议（`suggestions JSONB`） | 全 | ADR-0011 新增 |

### 面试模块表字段契约（ADR-0011）

- `interview_session`：`user_id`、`job_id NULL`（自由练习可空）、`occupation_role_id`、
  `status VARCHAR`、`started_at`、`finished_at`。
- `interview_question`：`session_id`、`question_type VARCHAR`（TECHNICAL/BEHAVIORAL/
  SITUATIONAL/RESUME_BASED）、`content TEXT`、`expected_points JSONB`、`order_no INT`、
  `is_bank_visible BOOLEAN DEFAULT false`（报告完成后题库可见）。
- `interview_answer`：`question_id`、`content TEXT`、`ai_score FLOAT(0~100)`、
  `ai_feedback TEXT`、`matched_points JSONB`、`missed_points JSONB`、`answered_at`。
- `interview_report`：`session_id`、`overall_score FLOAT(0~100)`、
  `radar JSONB`（`{communication, technical, problem_solving, culture_fit, depth}` 各 0~100）、
  `feedback JSONB`（`[{dimension, score, advice}]`）。
- `resume_optimization`：`resume_id`、`job_id NULL`、`suggestions JSONB`
  （`[{section, current, suggestion, relates_to_skill}]`）。

## 与旧版的差异（V4 对齐）

- **`role` → `occupation_role`**（V4 Q11）：消除与 `user.role`（用户角色字段）的同名冲突。
  `role_skill` → `occupation_role_skill`。`job` 加 `occupation_role_id` 挂联职业角色。
  用户角色保持 `user.role` 字段不变（枚举常量 ADMIN/USER/COMPANY）。
- **`company` + `audit_status` + `audit_reason`**（V4 Q19）：企业资质审核流程。
- **`user_profile` + `profile_completeness`**（V4 Q19）：简历完成度。
- **`recommend_record` + `is_invited`**（V4 Q16）：企业方发起面试邀请记录。
- **`notification` + `is_read` + `type`**（V4 Q18）：已读状态 + 通知类型枚举。
- **`parse_task.status` + `REJECTED`**（V4 Q12）：伪文件即拒。
- **`job` + `source`（MANUAL/UPLOAD）**（V4 Q12）：JD 手动填写 vs 文件上传双模式。
- **`skill` + `category`**（V4 Q21）：技能领域标签，community detection 兜底。
- **`resume`/`job` + `embedding_cache JSONB`**（V4 Q2）：embedding 落库缓存。
- **`match_result` 新鲜度口径**（V4 Q1）：按 (resume_id, job_id) 懒计算 +
  `updated_at` 晚于技能最后变更则直接返回。
- **`career_plan` 字段契约**（V4 Q6）：结构化 JSON + LLM 润色句列，删薪资预测。
- **03_seed 规模**（V4 Q4/Q11/Q21）：80~120 条 ACTIVE 技能 + 8~12 条 occupation_role +
  ≥15 条 skill_synonym + ≥10 条 skill_relation 示例边。

## 面试模块增量（ADR-0011）

- **5 张新表**（#23~#27）：面试会话 / 面试问题 / 用户回答 / 面试报告 / 简历优化建议。
- **`interview_question.is_bank_visible`**：报告生成后题目可入题库页复用。
  面试题纯由 AI 据 JD + occupation_role 技能生成，不爬外部题库（合规红线）。
- **`interview_report.radar` 与 `match_detail` 对齐**：technical 吸收 skill 子分，
  communication/problem_solving 由回答 AI 评产出，culture_fit 由 JD 关键词 + 回答匹配，
  depth 由 PREREQUISITE 链深度推断（复用既有图算法）。
- **面试反馈 → 学习路径**：gap 技能集直接喂入既有职业规划管线（V4 Q6），
  不另写一套；`career_plan` 以可选 `source VARCHAR(INTERVIEW/PROACTIVE/RECOMMEND)` 标来源。
- 语音情感/视频微表情多模态不在本期表与代码口径内，标为愿景（ADR-0011 D1）。
