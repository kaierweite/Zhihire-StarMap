-- ============================================================
-- 智聘星图数据库建表脚本（01_schema.sql）
-- 数据库：KingbaseES V8 R6（PostgreSQL 兼容模式）
-- 表数量：27 张（22 基础 + 5 面试模块 ADR-0011）
-- 约定：
--   - 主键 BIGSERIAL
--   - 状态字段 VARCHAR 大写语义枚举（ADR-0002）
--   - 业务表含 created_at / updated_at / deleted_at
--   - 日志类 append-only 表仅 created_at + deleted_at
--   - deleted_at 为 VARCHAR("0"未删/"1"已删)，对齐 MyBatis-Plus 逻辑删除
-- ============================================================

-- ==================== 第一批：基础表（无外键依赖） ====================

-- #1 用户主表
CREATE TABLE "user" (
    id            BIGSERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL,
    password      VARCHAR(255) NOT NULL,
    email         VARCHAR(100),
    phone         VARCHAR(20),
    role          VARCHAR(20)  NOT NULL DEFAULT 'USER',    -- ADMIN/USER/COMPANY
    status        VARCHAR(20)  NOT NULL DEFAULT 'NORMAL',  -- NORMAL/DISABLED/BANNED
    avatar_url    VARCHAR(500),
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at    VARCHAR(1)   NOT NULL DEFAULT '0'        -- "0"未删/"1"已删
);

COMMENT ON TABLE  "user"              IS '用户主表';
COMMENT ON COLUMN "user".role         IS '用户角色：ADMIN/USER/COMPANY';
COMMENT ON COLUMN "user".status       IS '账户状态：NORMAL/DISABLED/BANNED';
COMMENT ON COLUMN "user".deleted_at   IS '逻辑删除标记：0未删/1已删';

-- #15 文件本体（单一事实源）
CREATE TABLE upload_file (
    id            BIGSERIAL PRIMARY KEY,
    original_name VARCHAR(255) NOT NULL,
    stored_name   VARCHAR(255) NOT NULL,
    path          VARCHAR(500) NOT NULL,
    size          BIGINT       NOT NULL,
    mime_type     VARCHAR(100),
    uploader_id   BIGINT       NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at    VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE upload_file IS '文件本体表（单一事实源）';

-- #6 技能字典
CREATE TABLE skill (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(50),                           -- 后端/前端/测试/运维/数据/通用
    description     TEXT,
    status          VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE', -- ACTIVE/CANDIDATE/MERGED
    merge_target_id BIGINT,                                -- MERGED 时指向目标技能
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at      VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  skill            IS '技能字典';
COMMENT ON COLUMN skill.status     IS '技能状态：ACTIVE/CANDIDATE/MERGED';
COMMENT ON COLUMN skill.category   IS '技能领域：后端/前端/测试/运维/数据/通用';

-- #20 职业角色（V4 Q11 从 role 重命名，区别于 user.role）
CREATE TABLE occupation_role (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL,
    description TEXT,
    category    VARCHAR(50),
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE occupation_role IS '职业角色（后端开发/前端开发/测试工程师等）';

-- #14 通知
CREATE TABLE notification (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT       NOT NULL,
    title      VARCHAR(200) NOT NULL,
    content    TEXT,
    type       VARCHAR(30)  NOT NULL DEFAULT 'SYSTEM', -- APPLICATION/INTERVIEW_INVITE/SYSTEM
    is_read    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  notification       IS '通知表';
COMMENT ON COLUMN notification.type  IS '通知类型：APPLICATION/INTERVIEW_INVITE/SYSTEM';

-- ==================== 第二批：关联表（依赖第一批） ====================

-- #2 求职者档案
CREATE TABLE user_profile (
    id                   BIGSERIAL PRIMARY KEY,
    user_id              BIGINT       NOT NULL,
    real_name            VARCHAR(50),
    gender               VARCHAR(10),                     -- MALE/FEMALE/OTHER
    birth_date           DATE,
    education            VARCHAR(20),                     -- 高中/专科/本科/硕士/博士
    school               VARCHAR(100),
    major                VARCHAR(100),
    work_years           INT,
    expected_salary_min  DECIMAL(12,2),
    expected_salary_max  DECIMAL(12,2),
    expected_city        VARCHAR(100),
    current_city         VARCHAR(100),
    bio                  TEXT,
    profile_completeness INT          DEFAULT 0,          -- 0~100 完成度
    created_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at           VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  user_profile                    IS '求职者档案';
COMMENT ON COLUMN user_profile.profile_completeness IS '简历完成度 0~100';

-- #3 企业档案
CREATE TABLE company (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT       NOT NULL,
    company_name  VARCHAR(200) NOT NULL,
    industry      VARCHAR(100),
    scale         VARCHAR(50),                           -- 1-50人/50-150人/150-500人/500人以上
    website       VARCHAR(500),
    logo_url      VARCHAR(500),
    description   TEXT,
    address       VARCHAR(500),
    contact_name  VARCHAR(50),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    audit_status  VARCHAR(20)  NOT NULL DEFAULT 'UNVERIFIED', -- UNVERIFIED/PENDING/VERIFIED/REJECTED
    audit_reason  TEXT,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at    VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  company              IS '企业档案';
COMMENT ON COLUMN company.audit_status IS '审核状态：UNVERIFIED/PENDING/VERIFIED/REJECTED';

-- #4 简历实体
CREATE TABLE resume (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT       NOT NULL,
    file_id         BIGINT,                              -- FK → upload_file.id
    title           VARCHAR(200),
    content_text    TEXT,
    embedding_cache JSONB,                               -- embedding 向量缓存
    status          VARCHAR(20)  NOT NULL DEFAULT 'NORMAL', -- NORMAL/DISABLED
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at      VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE resume IS '简历实体';

-- #16 解析任务
CREATE TABLE parse_task (
    id          BIGSERIAL PRIMARY KEY,
    file_id     BIGINT       NOT NULL,                  -- FK → upload_file.id
    user_id     BIGINT       NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'WAITING', -- WAITING/PARSING/SUCCESS/FAILED/REJECTED
    result      JSONB,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  parse_task        IS '文档解析任务';
COMMENT ON COLUMN parse_task.status IS '任务状态：WAITING/PARSING/SUCCESS/FAILED/REJECTED';

-- #5 岗位
CREATE TABLE job (
    id                 BIGSERIAL PRIMARY KEY,
    company_id         BIGINT       NOT NULL,
    occupation_role_id BIGINT,                              -- FK → occupation_role.id
    title              VARCHAR(200) NOT NULL,
    description        TEXT,
    requirements       TEXT,
    salary_min         DECIMAL(12,2),
    salary_max         DECIMAL(12,2),
    city               VARCHAR(100),
    experience_min     INT,
    education_requirement VARCHAR(20),
    job_type           VARCHAR(20)  NOT NULL DEFAULT 'FULL_TIME', -- FULL_TIME/PART_TIME/INTERN
    status             VARCHAR(20)  NOT NULL DEFAULT 'OPEN',      -- OPEN/CLOSED/DRAFT
    source             VARCHAR(20)  NOT NULL DEFAULT 'MANUAL',    -- MANUAL/UPLOAD
    embedding_cache    JSONB,
    created_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at         VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  job         IS '岗位表';
COMMENT ON COLUMN job.status  IS '岗位状态：OPEN/CLOSED/DRAFT';
COMMENT ON COLUMN job.source  IS '岗位来源：MANUAL手动/UPLOAD文件上传';

-- #7 用户与技能关联
CREATE TABLE user_skill (
    id               BIGSERIAL PRIMARY KEY,
    user_id          BIGINT  NOT NULL,
    skill_id         BIGINT  NOT NULL,
    proficiency_level FLOAT   DEFAULT 0,                   -- 0~5 熟练度
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at       VARCHAR(1) NOT NULL DEFAULT '0'
);

COMMENT ON TABLE user_skill IS '用户技能关联';

-- #8 岗位与技能关联
CREATE TABLE job_skill (
    id             BIGSERIAL PRIMARY KEY,
    job_id         BIGINT       NOT NULL,
    skill_id       BIGINT       NOT NULL,
    importance     FLOAT        DEFAULT 3,                  -- 1~5 重要度
    required_level VARCHAR(20)  DEFAULT 'NICE',            -- MUST/NICE/BONUS
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at     VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  job_skill              IS '岗位技能关联';
COMMENT ON COLUMN job_skill.importance   IS '重要度 1~5';
COMMENT ON COLUMN job_skill.required_level IS '要求等级：MUST/NICE/BONUS';

-- #19 技能边表
CREATE TABLE skill_relation (
    id              BIGSERIAL PRIMARY KEY,
    skill_id        BIGINT       NOT NULL,
    related_skill_id BIGINT      NOT NULL,
    relation_type   VARCHAR(30)  NOT NULL,                 -- PREREQUISITE/SIMILAR/INCLUDES/COMPLEMENTARY
    weight          FLOAT        DEFAULT 1.0,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at      VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  skill_relation             IS '技能关系边表';
COMMENT ON COLUMN skill_relation.relation_type IS '关系类型：PREREQUISITE/SIMILAR/INCLUDES/COMPLEMENTARY';

-- #22 技能同义词
CREATE TABLE skill_synonym (
    id        BIGSERIAL PRIMARY KEY,
    skill_id  BIGINT       NOT NULL,                      -- FK → skill.id
    synonym   VARCHAR(100) NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE skill_synonym IS '技能同义词（支撑三态合并）';

-- #21 角色技能关联
CREATE TABLE occupation_role_skill (
    id                 BIGSERIAL PRIMARY KEY,
    occupation_role_id BIGINT       NOT NULL,              -- FK → occupation_role.id
    skill_id           BIGINT       NOT NULL,              -- FK → skill.id
    requirement_level  VARCHAR(20)  NOT NULL DEFAULT 'NICE', -- MUST/NICE/BONUS
    created_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at         VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  occupation_role_skill               IS '职业角色技能关联';
COMMENT ON COLUMN occupation_role_skill.requirement_level IS '要求等级：MUST/NICE/BONUS';

-- #9 匹配结果（双向共用）
CREATE TABLE match_result (
    id          BIGSERIAL PRIMARY KEY,
    resume_id   BIGINT       NOT NULL,
    job_id      BIGINT       NOT NULL,
    score       FLOAT        DEFAULT 0,                   -- 0~100 匹配分
    match_detail JSONB,                                    -- 匹配明细（含 rationale）
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE match_result IS '匹配结果（懒计算 + 新鲜度缓存）';

-- #10 推荐记录
CREATE TABLE recommend_record (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT   NOT NULL,
    job_id      BIGINT   NOT NULL,
    score       FLOAT    DEFAULT 0,
    is_clicked  BOOLEAN  DEFAULT FALSE,
    is_applied  BOOLEAN  DEFAULT FALSE,
    is_invited  BOOLEAN  DEFAULT FALSE,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  VARCHAR(1) NOT NULL DEFAULT '0'
);

COMMENT ON TABLE recommend_record IS '推荐记录';

-- #11 职业规划
CREATE TABLE career_plan (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT       NOT NULL,
    target_role   VARCHAR(100),
    plan_content  JSONB,                                   -- {target_role, gap_skills[], learning_path[], ...}
    source        VARCHAR(20)  DEFAULT 'PROACTIVE',        -- INTERVIEW/PROACTIVE/RECOMMEND
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at    VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  career_plan        IS '职业规划';
COMMENT ON COLUMN career_plan.source IS '规划来源：INTERVIEW/PROACTIVE/RECOMMEND';

-- #17 图谱渲染缓存（非图谱本体，权威在 AI 内存）
CREATE TABLE ability_graph (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT       NOT NULL,
    graph_data  JSONB,                                     -- 图谱渲染数据
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE ability_graph IS '能力图谱渲染缓存';

-- #18 AI 对话历史
CREATE TABLE ai_chat_history (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT       NOT NULL,
    module     VARCHAR(30),                                -- career/resume/interview
    role       VARCHAR(20)  NOT NULL,                      -- user/assistant
    content    TEXT         NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE ai_chat_history IS 'AI 对话历史';

-- #12 登录日志（append-only，仅 created_at + deleted_at）
CREATE TABLE login_log (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT       NOT NULL,
    ip         VARCHAR(50),
    user_agent VARCHAR(500),
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE login_log IS '登录日志（append-only）';

-- #13 操作日志（append-only，仅 created_at + deleted_at）
CREATE TABLE operation_log (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT       NOT NULL,
    module     VARCHAR(50),
    action     VARCHAR(100),
    detail     JSONB,
    ip         VARCHAR(50),
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE operation_log IS '操作日志（AOP @OperationLog 落库）';

-- ==================== 第三批：面试模块表（ADR-0011） ====================

-- #23 面试会话
CREATE TABLE interview_session (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT       NOT NULL,
    job_id              BIGINT,                            -- 自由练习可空
    occupation_role_id  BIGINT,
    status              VARCHAR(20)  NOT NULL DEFAULT 'PENDING', -- PENDING/IN_PROGRESS/COMPLETED/ABORTED
    started_at          TIMESTAMP,
    finished_at         TIMESTAMP,
    created_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  interview_session        IS '面试会话';
COMMENT ON COLUMN interview_session.status IS '会话状态：PENDING/IN_PROGRESS/COMPLETED/ABORTED';

-- #24 面试问题
CREATE TABLE interview_question (
    id              BIGSERIAL PRIMARY KEY,
    session_id      BIGINT       NOT NULL,                -- FK → interview_session.id
    question_type   VARCHAR(30)  NOT NULL,                 -- TECHNICAL/BEHAVIORAL/SITUATIONAL/RESUME_BASED
    content         TEXT         NOT NULL,
    expected_points JSONB,
    order_no        INT          NOT NULL DEFAULT 0,
    is_bank_visible BOOLEAN      NOT NULL DEFAULT FALSE,  -- 报告完成后题库可见
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at      VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  interview_question                IS '面试问题';
COMMENT ON COLUMN interview_question.question_type  IS '题型：TECHNICAL/BEHAVIORAL/SITUATIONAL/RESUME_BASED';
COMMENT ON COLUMN interview_question.is_bank_visible IS '报告完成后是否题库可见';

-- #25 用户回答
CREATE TABLE interview_answer (
    id             BIGSERIAL PRIMARY KEY,
    question_id    BIGINT       NOT NULL,                 -- FK → interview_question.id
    content        TEXT,
    ai_score       FLOAT,                                 -- 0~100 AI 评分
    ai_feedback    TEXT,
    matched_points JSONB,
    missed_points  JSONB,
    answered_at    TIMESTAMP,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at     VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  interview_answer       IS '用户面试回答';
COMMENT ON COLUMN interview_answer.ai_score IS 'AI 评分 0~100';

-- #26 面试报告
CREATE TABLE interview_report (
    id            BIGSERIAL PRIMARY KEY,
    session_id    BIGINT       NOT NULL,                  -- FK → interview_session.id
    overall_score FLOAT,                                   -- 0~100 综合分
    radar         JSONB,                                   -- {communication, technical, problem_solving, culture_fit, depth}
    feedback      JSONB,                                   -- [{dimension, score, advice}]
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at    VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE  interview_report           IS '面试报告';
COMMENT ON COLUMN interview_report.radar     IS '五维雷达：communication/technical/problem_solving/culture_fit/depth';
COMMENT ON COLUMN interview_report.overall_score IS '综合评分 0~100';

-- #27 简历优化建议
CREATE TABLE resume_optimization (
    id          BIGSERIAL PRIMARY KEY,
    resume_id   BIGINT       NOT NULL,                    -- FK → resume.id
    job_id      BIGINT,                                   -- 针对特定岗位可空
    suggestions JSONB,                                     -- [{section, current, suggestion, relates_to_skill}]
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  VARCHAR(1)   NOT NULL DEFAULT '0'
);

COMMENT ON TABLE resume_optimization IS '简历优化建议';
