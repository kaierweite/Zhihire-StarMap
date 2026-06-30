# 第2天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

完成数据库详细设计，包括所有表结构、字段设计、索引设计和ER图。

## 今日能力要求

- SQL（熟练）
- 数据库设计（熟练）

**最终产出：**

```text
database/
├── schema.sql              # 完整建表SQL（19张表）
├── index.sql               # 索引优化SQL
├── seed.sql                # 初始化测试数据
├── ER-v1.drawio            # ER图源文件
├── ER-v1.png               # ER图导出
├── ER-v1.pdf               # ER图PDF
├── entities.md             # 实体设计文档（完整字段定义）
└── 数据库设计说明.md        # 设计文档
```

---

# 第一阶段：表结构详细设计（3小时）

## 参考依据

所有表结构以 `database/entities.md` 为最终规范，数据库选型为人大会金仓 KingbaseES V8R6（PostgreSQL兼容模式），共 **19张表**，分为7大模块。

---

## 任务1：用户模块（3张表）

### 1.1 user（用户认证表）

**说明**：存储所有用户的登录认证信息，通过 `role` 字段区分角色（ADMIN/USER/COMPANY）。

**核心字段**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 用户ID |
| username | VARCHAR(64) | NOT NULL, UNIQUE | 用户名 |
| password | VARCHAR(255) | NOT NULL | BCrypt加密密码 |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'USER' | ADMIN/USER/COMPANY |
| phone | VARCHAR(20) | | 手机号 |
| email | VARCHAR(100) | | 邮箱 |
| status | VARCHAR(20) | DEFAULT 'NORMAL' | NORMAL/DISABLED/BANNED |
| last_login_time | TIMESTAMP | | 最后登录时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMP | | 逻辑删除时间 |

**索引**：`idx_user_phone`、`idx_user_email`、`idx_user_role`

> **注意**：表名使用 `user`（加双引号），不是 `sys_user`。字段统一使用 `created_at`/`updated_at`/`deleted_at` 命名风格，状态字段使用 VARCHAR 语义化枚举（如 `NORMAL`/`DISABLED`），而非 INT 数字状态。

### 1.2 user_profile（用户个人资料表）

**说明**：存储用户的详细个人资料，与 `user` 表一对一关系。用户的教育背景、工作年限、意向城市等资料存储在此表，不单独拆分教育/工作/项目经历子表（简历中的详细经历以 JSONB 存储在 `resume.parsed_data` 中）。

**核心字段**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 资料ID |
| user_id | BIGINT | NOT NULL, UNIQUE, FK(user.id) | 关联用户ID |
| real_name | VARCHAR(50) | | 真实姓名 |
| gender | VARCHAR(10) | | 性别 |
| birthday | DATE | | 出生日期 |
| education | VARCHAR(50) | | 最高学历 |
| school | VARCHAR(100) | | 毕业院校 |
| major | VARCHAR(100) | | 专业 |
| work_year | INTEGER | DEFAULT 0 | 工作年限 |
| target_city | VARCHAR(50) | | 意向城市 |
| avatar | VARCHAR(255) | | 头像URL |
| introduction | TEXT | | 个人简介 |

### 1.3 company（企业信息表）

**说明**：存储企业详细信息，与 `user` 表一对一关系。当前采用单企业管理员模型。

**核心字段**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 企业ID |
| user_id | BIGINT | NOT NULL, UNIQUE, FK(user.id) | 关联用户ID |
| company_name | VARCHAR(100) | NOT NULL | 企业名称 |
| credit_code | VARCHAR(50) | | 统一社会信用代码 |
| industry | VARCHAR(50) | | 所属行业 |
| scale | VARCHAR(50) | | 公司规模 |
| description | TEXT | | 公司简介 |
| website | VARCHAR(255) | | 官网地址 |
| address | VARCHAR(255) | | 公司地址 |
| logo | VARCHAR(255) | | Logo URL |

> **扩展性说明**：后续可扩展为多HR子账号模式。

---

## 任务2：简历模块（1张表）

### 2.1 resume（简历表）

**说明**：存储用户上传的简历文件及AI解析结果。简历中的详细教育经历、工作经历、项目经历等不拆分子表，统一存入 `parsed_data(JSONB)` 字段，保持数据结构弹性。

**核心字段**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 简历ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 所属用户 |
| file_name | VARCHAR(255) | NOT NULL | 原始文件名 |
| file_path | VARCHAR(500) | | 文件存储路径 |
| file_url | VARCHAR(500) | | 文件访问URL |
| storage_type | VARCHAR(20) | DEFAULT 'LOCAL' | LOCAL/MINIO/OSS |
| file_type | VARCHAR(20) | | PDF/DOC/DOCX |
| parse_status | VARCHAR(20) | DEFAULT 'WAITING' | WAITING/PARSING/SUCCESS/FAILED |
| status | VARCHAR(20) | DEFAULT 'NORMAL' | NORMAL/DELETED/ARCHIVED |
| raw_text | TEXT | | 提取的纯文本全文 |
| parsed_data | JSONB | | AI解析结构化结果 |
| parse_time | TIMESTAMP | | 解析完成时间 |

**索引**：`idx_resume_user_id`、`idx_resume_status`、`idx_resume_parse_status`

> **设计考量**：不拆分 `resume_education`、`resume_work_experience`、`resume_project` 子表，原因如下：
> 1. 这些数据由AI解析产生，结构不固定
> 2. JSONB 可灵活存储不同简历的差异结构
> 3. 减少表关联查询复杂度
> 4. 后续需要独立查询教育/工作经历时，可以从 JSONB 中提取并物化

---

## 任务3：岗位模块（1张表）

### 3.1 job（岗位表）

**说明**：存储企业发布的岗位信息及AI解析结果。字段命名采用 `job_name`、`job_description`、`salary_min`、`salary_max`，薪资单位为 K。

**核心字段**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 岗位ID |
| company_id | BIGINT | NOT NULL, FK(company.id) | 发布企业 |
| job_name | VARCHAR(100) | NOT NULL | 岗位名称 |
| job_description | TEXT | | 岗位描述 |
| city | VARCHAR(50) | | 工作城市 |
| education_required | VARCHAR(50) | | 学历要求 |
| experience_required | VARCHAR(50) | | 经验要求 |
| salary_min | INTEGER | | 最低薪资（K） |
| salary_max | INTEGER | | 最高薪资（K） |
| department | VARCHAR(100) | | 所属部门 |
| is_urgent | BOOLEAN | DEFAULT FALSE | 是否紧急 |
| view_count | INTEGER | DEFAULT 0 | 浏览次数 |
| status | VARCHAR(20) | DEFAULT 'OPEN' | OPEN/CLOSED/DRAFT |

**索引**：`idx_job_company_id`、`idx_job_city`、`idx_job_status`、`idx_job_is_urgent`

> **注意**：不创建 `job_requirement_detail` 子表，岗位要求通过 `job_skill` 关联技能表实现结构化存储，详细要求文本存入 `job_description`。

---

## 任务4：技能模块（3张表）

### 4.1 skill（技能字典表）

**说明**：技能字典，支持多级分类（通过 `parent_id` 自引用），如 Java(level=1) → Spring Boot(level=2, parent_id=Java.id)。

**核心字段**：

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 技能ID |
| name | VARCHAR(100) | NOT NULL, UNIQUE | 技能名称 |
| category | VARCHAR(50) | | 技能分类（Backend/AI/Frontend等） |
| level | INTEGER | DEFAULT 1 | 层级（1一级/2二级） |
| parent_id | BIGINT | FK(skill.id) | 父级技能ID |
| description | TEXT | | 技能描述 |

### 4.2 user_skill（用户技能关联表）

**说明**：用户与技能的多对多关联，记录掌握程度和年限。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 关联ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 用户ID |
| skill_id | BIGINT | NOT NULL, FK(skill.id) | 技能ID |
| proficiency | VARCHAR(20) | | BEGINNER/INTERMEDIATE/ADVANCED/EXPERT |
| years | INTEGER | DEFAULT 0 | 经验年限 |

**索引**：`idx_user_skill_user_id`、`idx_user_skill_skill_id`

### 4.3 job_skill（岗位技能关联表）

**说明**：岗位与技能的多对多关联，记录重要程度。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 关联ID |
| job_id | BIGINT | NOT NULL, FK(job.id) | 岗位ID |
| skill_id | BIGINT | NOT NULL, FK(skill.id) | 技能ID |
| importance | INTEGER | DEFAULT 5 | 重要程度（1-10） |

**索引**：`idx_job_skill_job_id`、`idx_job_skill_skill_id`

---

## 任务5：匹配模块（2张表）

### 5.1 match_result（匹配结果表）

**说明**：存储用户简历与岗位的AI匹配结果，`match_detail(JSONB)` 存储详细的技能维度匹配分析。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 匹配ID |
| resume_id | BIGINT | NOT NULL, FK(resume.id) | 简历ID |
| job_id | BIGINT | NOT NULL, FK(job.id) | 岗位ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 用户ID |
| match_score | DECIMAL(5,2) | | 匹配分数 |
| match_detail | JSONB | | 匹配详情（各技能维度分数） |
| match_summary | TEXT | | 匹配摘要 |
| status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING/PROCESSING/COMPLETED/FAILED |

**索引**：`idx_match_result_resume_id`、`idx_match_result_job_id`、`idx_match_result_user_id`、`idx_match_result_score`、**`uq_match_result_resume_job`**

> **注意**：`resume_id` + `job_id` 建立联合唯一索引，防止重复匹配。

### 5.2 recommend_record（推荐记录表）

**说明**：存储系统推荐记录，支持岗位推荐（JOB）和人才推荐（TALENT）。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 推荐ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 用户ID |
| match_result_id | BIGINT | NOT NULL, FK(match_result.id) | 关联匹配结果 |
| recommend_type | VARCHAR(20) | NOT NULL | JOB/TALENT/SYSTEM |
| reason | TEXT | | 推荐理由 |
| status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING/VIEWED/APPLIED/IGNORED |

---

## 任务6：职业发展模块（4张表）

### 6.1 career_plan（职业规划表）

**说明**：存储用户的AI职业规划建议。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 规划ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 用户ID |
| plan_name | VARCHAR(100) | | 规划名称 |
| target_role | VARCHAR(100) | | 目标岗位 |
| current_skills | JSONB | | 当前技能现状 |
| target_skills | JSONB | | 目标技能要求 |
| gap_analysis | JSONB | | 差距分析 |
| plan_content | TEXT | | 规划内容 |
| plan_data | JSONB | | 规划扩展数据 |
| status | VARCHAR(20) | DEFAULT 'DRAFT' | DRAFT/ACTIVE/COMPLETED |

### 6.2 interview_question（面试题表）

**说明**：存储AI生成的各岗位面试题目，支持按技能和难度分类。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 题目ID |
| job_id | BIGINT | NOT NULL, FK(job.id) | 所属岗位 |
| skill_id | BIGINT | FK(skill.id) | 关联技能 |
| question_type | VARCHAR(20) | | TECHNICAL/BEHAVIORAL/SYSTEM_DESIGN |
| question | TEXT | NOT NULL | 题目内容 |
| difficulty | VARCHAR(20) | | EASY/MEDIUM/HARD |

### 6.3 ability_graph（能力图谱表）

**说明**：缓存用户或岗位的能力图谱数据（ECharts格式），通过 `graph_type` 区分 USER 图谱和 JOB 图谱。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 图谱ID |
| user_id | BIGINT | FK(user.id) | 用户ID（graph_type=USER时必填） |
| job_id | BIGINT | FK(job.id) | 岗位ID（graph_type=JOB时必填） |
| graph_type | VARCHAR(20) | NOT NULL | USER/JOB |
| graph_name | VARCHAR(100) | | 图谱名称 |
| version | VARCHAR(20) | DEFAULT 'v1' | 版本号 |
| graph_status | VARCHAR(20) | DEFAULT 'SUCCESS' | GENERATING/SUCCESS/FAILED |
| graph_data | JSONB | | 图谱数据（ECharts格式） |

**索引**：`idx_ability_graph_user_id`、`idx_ability_graph_job_id`

### 6.4 ai_chat_history（AI对话历史表）

**说明**：记录用户与AI助手的对话历史，用于职业规划、简历优化等场景。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 对话ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 用户ID |
| session_id | VARCHAR(64) | | 会话ID |
| message_type | VARCHAR(20) | NOT NULL | USER/ASSISTANT/SYSTEM |
| content | TEXT | NOT NULL | 对话内容 |
| extra_data | JSONB | | 扩展信息（tokens、model等） |

---

## 任务7：系统管理模块（5张表）

### 7.1 notification（通知表）

**说明**：存储系统通知消息。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 通知ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 接收用户 |
| title | VARCHAR(200) | NOT NULL | 通知标题 |
| content | TEXT | | 通知内容 |
| type | VARCHAR(20) | DEFAULT 'SYSTEM' | SYSTEM/RECOMMEND/APPLICATION/INTERVIEW |
| is_read | BOOLEAN | DEFAULT FALSE | 是否已读 |

### 7.2 login_log（登录日志表）

**说明**：记录用户登录日志。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 日志ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 用户ID |
| login_time | TIMESTAMP | | 登录时间 |
| ip_address | VARCHAR(50) | | 登录IP |
| device | VARCHAR(100) | | 登录设备 |
| login_result | VARCHAR(20) | | SUCCESS/FAILED |
| fail_reason | VARCHAR(100) | | 失败原因 |

**索引**：`idx_login_log_user_id`、`idx_login_log_login_time`

### 7.3 operation_log（操作日志表）

**说明**：记录用户操作日志。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 日志ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 操作用户 |
| module | VARCHAR(50) | | 操作模块 |
| action | VARCHAR(50) | | 操作动作 |
| target_id | BIGINT | | 操作对象ID |
| detail | TEXT | | 操作详情 |
| ip_address | VARCHAR(50) | | 操作IP |

**索引**：`idx_operation_log_user_id`

### 7.4 upload_file（文件上传记录表）

**说明**：记录所有用户上传的文件信息。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 文件ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 上传用户 |
| file_name | VARCHAR(255) | NOT NULL | 原始文件名 |
| file_path | VARCHAR(500) | | 存储路径 |
| file_url | VARCHAR(500) | | 访问URL |
| storage_type | VARCHAR(20) | DEFAULT 'LOCAL' | LOCAL/MINIO/OSS |
| file_size | BIGINT | | 文件大小 |
| file_type | VARCHAR(50) | | 文件类型 |
| md5 | VARCHAR(64) | | 文件MD5 |

### 7.5 parse_task（解析任务表）

**说明**：管理AI解析任务的状态和结果。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 任务ID |
| user_id | BIGINT | NOT NULL, FK(user.id) | 所属用户 |
| file_id | BIGINT | NOT NULL, FK(upload_file.id) | 关联文件 |
| task_type | VARCHAR(20) | NOT NULL | RESUME_PARSE/JOB_PARSE/SKILL_EXTRACT |
| status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING/PROCESSING/SUCCESS/FAILED |
| result | JSONB | | 解析结果 |
| error_message | TEXT | | 错误信息 |
| retry_count | INTEGER | DEFAULT 0 | 重试次数 |

**索引**：`idx_parse_task_status`、`idx_parse_task_user_id`

---

# 第二阶段：索引优化与SQL编写（2小时）

## 索引设计总览

详见 `database/index.sql`，索引覆盖以下维度：

- **用户模块**：phone、email、role
- **简历模块**：user_id、status、parse_status、GIN全文索引
- **岗位模块**：company_id、city、status、is_urgent、GIN全文索引
- **技能关联**：user_skill(user_id/skill_id)、job_skill(job_id/skill_id)
- **匹配模块**：resume_id、job_id、user_id、match_score（DESC）、联合唯一索引
- **职业发展**：ability_graph(user_id/job_id)
- **系统管理**：login_log(user_id/login_time)、operation_log(user_id)、parse_task(status/user_id)

## 建表SQL

完整建表SQL见 `database/schema.sql`，需要严格按 `database/entities.md` 中定义的字段、类型、约束、索引来编写。

## ER图绘制要求

- 使用 draw.io
- 标注主键（PK）和外键（FK）
- 标注字段类型和长度
- 标注是否允许为 NULL
- 标注索引

现有 ER 图文件：`database/ER-v1.drawio`、`database/ER-v1.png`、`database/ER-v1.pdf`

---

# 第三阶段：测试数据准备（1小时）

## 初始化数据

详见 `database/seed.sql`，包含：

1. **用户数据**：1个管理员 + 3个求职者（张三/李四/王五） + 3个企业账号
2. **用户资料**：关联各求职者的详细资料
3. **企业信息**：字节跳动/阿里巴巴/腾讯
4. **技能字典**：7大类一级技能 + 19个二级技能
5. **岗位数据**：6个岗位（每个企业2个）
6. **用户技能关联**：每个用户掌握多个技能及熟练度
7. **岗位技能关联**：每个岗位关联多个技能及重要程度
8. **通知数据**：新用户欢迎通知

---

# 第四阶段：编写数据库设计文档（30分钟）

## 设计文档内容

详见 `database/数据库设计说明.md`，目录结构：

```text
1. 设计概述
   1.1 数据库选型（KingbaseES/PostgreSQL）
   1.2 设计原则
   1.3 命名规范

2. 表结构详细说明
   2.1 用户模块表（user/user_profile/company）
   2.2 简历模块表（resume）
   2.3 岗位模块表（job）
   2.4 技能模块表（skill/user_skill/job_skill）
   2.5 匹配模块表（match_result/recommend_record）
   2.6 职业发展模块表（career_plan/interview_question/ability_graph/ai_chat_history）
   2.7 系统管理表（notification/login_log/operation_log/upload_file/parse_task）

3. 索引设计
   3.1 主键索引
   3.2 普通索引
   3.3 联合索引
   3.4 全文索引

4. 约束设计
   4.1 主键约束
   4.2 外键约束
   4.3 CHECK约束
   4.4 唯一约束

5. 数据字典
   5.1 状态码定义
   5.2 角色定义
   5.3 枚举值说明

6. 实体关系汇总
   6.1 表间关联关系（23条关系）
   6.2 ER图
```

---

# 第2天验收标准

必须完成：

✅ 19张表全部设计完成（按 entities.md 规范）

✅ 建表SQL文件（schema.sql）— 严格对应 entities.md 的字段/类型/约束

✅ 索引SQL文件（index.sql）— 包含所有索引和全文检索索引

✅ 初始化数据SQL（seed.sql）— 覆盖核心业务场景

✅ ER图已完成（drawio/png/pdf）

✅ 数据库设计文档已输出（数据库设计说明.md）

✅ 经过至少1次评审修改

---

# 常见问题（FAQ）

**Q：为什么选KingbaseES（PostgreSQL兼容）而不是MySQL？**

A：KingbaseES兼容PostgreSQL生态，PG对JSONB支持和全文检索更适合AI场景，同时满足国产化要求。

**Q：为什么要用JSONB而不是拆子表？**

A：AI解析结果结构不确定，JSONB可以灵活存储不同简历/岗位的差异结构，减少表关联。

**Q：user表为什么要用 `"user"` 加引号？**

A：user是PostgreSQL/KingbaseES的保留关键字，需要使用双引号转义。

**Q：为什么是19张表而不是13张？**

A：相比简化设计，本设计增加了 `upload_file`（文件管理）、`parse_task`（解析任务管理）、`interview_question`（面试题库）、`ability_graph`（能力图谱缓存）、`ai_chat_history`（AI对话记录）、`notification`（通知管理）等表，覆盖完整业务链路。

**Q：状态字段为什么用VARCHAR不用INT？**

A：VARCHAR语义化枚举值（如 NORMAL/DISABLED/BANNED）可读性更好，排查问题时无需查映射表。

**Q：外键会不会影响性能？**

A：正式环境可以删除外键约束，保留逻辑关联。开发阶段保留外键保证数据一致性。

**Q：seed.sql中的密码怎么处理？**

A：使用BCrypt加密的占位密码，实际部署时需替换为真实加密值。
