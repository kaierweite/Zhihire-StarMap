-- ============================================================
-- 智聘星图数据库索引脚本（02_index.sql）
-- 执行顺序：在 01_schema.sql 之后
-- ============================================================

-- ==================== 唯一索引 ====================

-- user.username 唯一索引（登录名不可重复）
CREATE UNIQUE INDEX idx_user_username ON "user" (username) WHERE deleted_at = '0';

-- skill.name 唯一索引（归一查表兜底）
CREATE UNIQUE INDEX idx_skill_name ON skill (name) WHERE deleted_at = '0';

-- skill_synonym.synonym 唯一索引
CREATE UNIQUE INDEX idx_skill_synonym_synonym ON skill_synonym (synonym) WHERE deleted_at = '0';

-- match_result (resume_id, job_id) 联合唯一索引（懒计算兜底）
CREATE UNIQUE INDEX idx_match_result_resume_job ON match_result (resume_id, job_id) WHERE deleted_at = '0';

-- ==================== 查询索引 ====================

-- user 表
CREATE INDEX idx_user_role ON "user" (role) WHERE deleted_at = '0';
CREATE INDEX idx_user_status ON "user" (status) WHERE deleted_at = '0';

-- user_profile 表
CREATE INDEX idx_user_profile_user_id ON user_profile (user_id) WHERE deleted_at = '0';

-- company 表
CREATE INDEX idx_company_user_id ON company (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_company_audit_status ON company (audit_status) WHERE deleted_at = '0';

-- resume 表
CREATE INDEX idx_resume_user_id ON resume (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_resume_file_id ON resume (file_id) WHERE deleted_at = '0';

-- job 表
CREATE INDEX idx_job_company_id ON job (company_id) WHERE deleted_at = '0';
CREATE INDEX idx_job_occupation_role_id ON job (occupation_role_id) WHERE deleted_at = '0';
CREATE INDEX idx_job_status ON job (status) WHERE deleted_at = '0';
CREATE INDEX idx_job_city ON job (city) WHERE deleted_at = '0';

-- user_skill 表
CREATE INDEX idx_user_skill_user_id ON user_skill (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_user_skill_skill_id ON user_skill (skill_id) WHERE deleted_at = '0';

-- job_skill 表
CREATE INDEX idx_job_skill_job_id ON job_skill (job_id) WHERE deleted_at = '0';
CREATE INDEX idx_job_skill_skill_id ON job_skill (skill_id) WHERE deleted_at = '0';

-- skill_relation 表
CREATE INDEX idx_skill_relation_skill_id ON skill_relation (skill_id) WHERE deleted_at = '0';
CREATE INDEX idx_skill_relation_related ON skill_relation (related_skill_id) WHERE deleted_at = '0';

-- skill_synonym 表
CREATE INDEX idx_skill_synonym_skill_id ON skill_synonym (skill_id) WHERE deleted_at = '0';

-- occupation_role_skill 表
CREATE INDEX idx_ors_role_id ON occupation_role_skill (occupation_role_id) WHERE deleted_at = '0';
CREATE INDEX idx_ors_skill_id ON occupation_role_skill (skill_id) WHERE deleted_at = '0';

-- match_result 表
CREATE INDEX idx_match_result_resume_id ON match_result (resume_id) WHERE deleted_at = '0';
CREATE INDEX idx_match_result_job_id ON match_result (job_id) WHERE deleted_at = '0';
CREATE INDEX idx_match_result_score ON match_result (score) WHERE deleted_at = '0';

-- recommend_record 表
CREATE INDEX idx_recommend_user_id ON recommend_record (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_recommend_job_id ON recommend_record (job_id) WHERE deleted_at = '0';

-- career_plan 表
CREATE INDEX idx_career_plan_user_id ON career_plan (user_id) WHERE deleted_at = '0';

-- parse_task 表
CREATE INDEX idx_parse_task_file_id ON parse_task (file_id) WHERE deleted_at = '0';
CREATE INDEX idx_parse_task_user_id ON parse_task (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_parse_task_status ON parse_task (status) WHERE deleted_at = '0';

-- notification 表
CREATE INDEX idx_notification_user_id ON notification (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_notification_type ON notification (type) WHERE deleted_at = '0';
CREATE INDEX idx_notification_is_read ON notification (is_read) WHERE deleted_at = '0';

-- login_log 表（append-only）
CREATE INDEX idx_login_log_user_id ON login_log (user_id);

-- operation_log 表（append-only）
CREATE INDEX idx_operation_log_user_id ON operation_log (user_id);
CREATE INDEX idx_operation_log_module ON operation_log (module);

-- ai_chat_history 表
CREATE INDEX idx_ai_chat_user_id ON ai_chat_history (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_ai_chat_module ON ai_chat_history (module) WHERE deleted_at = '0';

-- ability_graph 表
CREATE INDEX idx_ability_graph_user_id ON ability_graph (user_id) WHERE deleted_at = '0';

-- upload_file 表
CREATE INDEX idx_upload_file_uploader ON upload_file (uploader_id);

-- ==================== 面试模块索引（ADR-0011） ====================

-- interview_session 表
CREATE INDEX idx_interview_session_user_id ON interview_session (user_id) WHERE deleted_at = '0';
CREATE INDEX idx_interview_session_job_id ON interview_session (job_id) WHERE deleted_at = '0';
CREATE INDEX idx_interview_session_status ON interview_session (status) WHERE deleted_at = '0';

-- interview_question 表
CREATE INDEX idx_interview_question_session ON interview_question (session_id) WHERE deleted_at = '0';

-- interview_answer 表
CREATE INDEX idx_interview_answer_question ON interview_answer (question_id) WHERE deleted_at = '0';

-- interview_report 表
CREATE INDEX idx_interview_report_session ON interview_report (session_id) WHERE deleted_at = '0';

-- resume_optimization 表
CREATE INDEX idx_resume_opt_resume_id ON resume_optimization (resume_id) WHERE deleted_at = '0';
CREATE INDEX idx_resume_opt_job_id ON resume_optimization (job_id) WHERE deleted_at = '0';
