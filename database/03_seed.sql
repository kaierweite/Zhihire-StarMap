-- ============================================================
-- 智聘星图种子数据（03_seed.sql）
-- 执行顺序：在 01_schema.sql + 02_index.sql 之后
-- 数据规模：
--   admin 账号 1 条
--   skill 100 条 ACTIVE
--   skill_synonym 20 条
--   occupation_role 10 条
--   occupation_role_skill ~60 条
--   skill_relation 25 条
-- ============================================================

-- ==================== 1. Admin 账号 ====================
-- 密码：admin123（BCrypt 加密）
INSERT INTO "user" (username, password, email, phone, role, status)
VALUES ('admin', '$2a$10$iTqJbcM.EgZQnklereeHTexX9qo8rXX4z6cFjZGfmtlr6kCqXdg2i', 'admin@zhihire.com', '13800000000', 'ADMIN', 'NORMAL');

-- ==================== 2. 技能字典（100 条 ACTIVE） ====================

-- 后端开发技能 (category='后端')
INSERT INTO skill (name, category, description, status) VALUES
('Java', '后端', 'Java 编程语言', 'ACTIVE'),
('Spring Boot', '后端', 'Spring Boot 框架', 'ACTIVE'),
('Spring Cloud', '后端', 'Spring Cloud 微服务框架', 'ACTIVE'),
('Spring MVC', '后端', 'Spring MVC Web 框架', 'ACTIVE'),
('MyBatis', '后端', 'MyBatis ORM 框架', 'ACTIVE'),
('MyBatis-Plus', '后端', 'MyBatis-Plus 增强框架', 'ACTIVE'),
('MySQL', '后端', 'MySQL 关系型数据库', 'ACTIVE'),
('PostgreSQL', '后端', 'PostgreSQL 关系型数据库', 'ACTIVE'),
('Redis', '后端', 'Redis 缓存数据库', 'ACTIVE'),
('MongoDB', '后端', 'MongoDB 文档数据库', 'ACTIVE'),
('RabbitMQ', '后端', 'RabbitMQ 消息队列', 'ACTIVE'),
('Kafka', '后端', 'Kafka 消息流平台', 'ACTIVE'),
('Docker', '后端', 'Docker 容器化', 'ACTIVE'),
('Kubernetes', '后端', 'Kubernetes 容器编排', 'ACTIVE'),
('Nginx', '后端', 'Nginx Web 服务器', 'ACTIVE'),
('Linux', '后端', 'Linux 操作系统', 'ACTIVE'),
('Git', '后端', 'Git 版本控制', 'ACTIVE'),
('Maven', '后端', 'Maven 构建工具', 'ACTIVE'),
('Gradle', '后端', 'Gradle 构建工具', 'ACTIVE'),
('JUnit', '后端', 'JUnit 单元测试框架', 'ACTIVE'),
('微服务架构', '后端', '微服务架构设计', 'ACTIVE'),
('RESTful API', '后端', 'RESTful 接口设计', 'ACTIVE'),
('SQL', '后端', 'SQL 查询语言', 'ACTIVE'),
('JDBC', '后端', 'Java 数据库连接', 'ACTIVE'),
('Hibernate', '后端', 'Hibernate ORM 框架', 'ACTIVE'),
('JPA', '后端', 'Java 持久化 API', 'ACTIVE'),
('Spring Security', '后端', 'Spring Security 安全框架', 'ACTIVE'),
('JWT', '后端', 'JSON Web Token 认证', 'ACTIVE'),
('GraphQL', '后端', 'GraphQL 查询语言', 'ACTIVE'),
('Elasticsearch', '后端', 'Elasticsearch 搜索引擎', 'ACTIVE'),

-- 前端开发技能 (category='前端')
('JavaScript', '前端', 'JavaScript 编程语言', 'ACTIVE'),
('TypeScript', '前端', 'TypeScript 编程语言', 'ACTIVE'),
('Vue.js', '前端', 'Vue.js 前端框架', 'ACTIVE'),
('React', '前端', 'React 前端框架', 'ACTIVE'),
('Angular', '前端', 'Angular 前端框架', 'ACTIVE'),
('HTML5', '前端', 'HTML5 标记语言', 'ACTIVE'),
('CSS3', '前端', 'CSS3 样式语言', 'ACTIVE'),
('Webpack', '前端', 'Webpack 构建工具', 'ACTIVE'),
('Vite', '前端', 'Vite 构建工具', 'ACTIVE'),
('Element Plus', '前端', 'Element Plus UI 组件库', 'ACTIVE'),
('Ant Design', '前端', 'Ant Design UI 组件库', 'ACTIVE'),
('ECharts', '前端', 'ECharts 数据可视化', 'ACTIVE'),
('Node.js', '前端', 'Node.js 运行时', 'ACTIVE'),
('npm', '前端', 'npm 包管理器', 'ACTIVE'),
('Pinia', '前端', 'Pinia 状态管理', 'ACTIVE'),
('Vuex', '前端', 'Vuex 状态管理', 'ACTIVE'),
('Vue Router', '前端', 'Vue Router 路由管理', 'ACTIVE'),
('Axios', '前端', 'Axios HTTP 客户端', 'ACTIVE'),
('Sass/LESS', '前端', 'CSS 预处理器', 'ACTIVE'),
('微信小程序', '前端', '微信小程序开发', 'ACTIVE'),

-- 测试技能 (category='测试')
('Selenium', '测试', 'Selenium 自动化测试', 'ACTIVE'),
('JMeter', '测试', 'JMeter 性能测试', 'ACTIVE'),
('Postman', '测试', 'Postman 接口测试', 'ACTIVE'),
('自动化测试', '测试', '自动化测试框架与实践', 'ACTIVE'),
('性能测试', '测试', '性能测试方法与工具', 'ACTIVE'),
('测试用例设计', '测试', '测试用例设计方法', 'ACTIVE'),
('缺陷管理', '测试', '缺陷跟踪与管理', 'ACTIVE'),
('Appium', '测试', 'Appium 移动端测试', 'ACTIVE'),
('Cypress', '测试', 'Cypress E2E 测试', 'ACTIVE'),
('CI/CD 测试', '测试', '持续集成中的测试', 'ACTIVE'),

-- 运维技能 (category='运维')
('Jenkins', '运维', 'Jenkins 持续集成', 'ACTIVE'),
('GitLab CI', '运维', 'GitLab CI/CD', 'ACTIVE'),
('Ansible', '运维', 'Ansible 自动化运维', 'ACTIVE'),
('Terraform', '运维', 'Terraform 基础设施即代码', 'ACTIVE'),
('Prometheus', '运维', 'Prometheus 监控系统', 'ACTIVE'),
('Grafana', '运维', 'Grafana 数据可视化', 'ACTIVE'),
('Zabbix', '运维', 'Zabbix 监控平台', 'ACTIVE'),
('Shell 脚本', '运维', 'Shell 脚本编程', 'ACTIVE'),
('云服务（AWS/阿里云）', '运维', '云计算平台运维', 'ACTIVE'),
('负载均衡', '运维', '负载均衡配置与优化', 'ACTIVE'),

-- 数据技能 (category='数据')
('Python', '数据', 'Python 编程语言', 'ACTIVE'),
('数据分析', '数据', '数据分析方法与工具', 'ACTIVE'),
('机器学习', '数据', '机器学习算法与应用', 'ACTIVE'),
('深度学习', '数据', '深度学习框架与应用', 'ACTIVE'),
('TensorFlow', '数据', 'TensorFlow 深度学习框架', 'ACTIVE'),
('PyTorch', '数据', 'PyTorch 深度学习框架', 'ACTIVE'),
('Pandas', '数据', 'Pandas 数据处理库', 'ACTIVE'),
('NumPy', '数据', 'NumPy 数值计算库', 'ACTIVE'),
('数据仓库', '数据', '数据仓库设计与实现', 'ACTIVE'),
('ETL', '数据', '数据抽取转换加载', 'ACTIVE'),
('Spark', '数据', 'Spark 大数据处理', 'ACTIVE'),
('Flink', '数据', 'Flink 实时流处理', 'ACTIVE'),
('Hadoop', '数据', 'Hadoop 大数据平台', 'ACTIVE'),
('数据可视化', '数据', '数据可视化工具与方法', 'ACTIVE'),
('NLP', '数据', '自然语言处理', 'ACTIVE'),
('大语言模型', '数据', 'LLM 大语言模型应用', 'ACTIVE'),

-- 通用技能 (category='通用')
('项目管理', '通用', '项目管理方法论', 'ACTIVE'),
('敏捷开发', '通用', 'Scrum/Kanban 敏捷方法', 'ACTIVE'),
('需求分析', '通用', '需求分析与管理', 'ACTIVE'),
('技术文档', '通用', '技术文档编写', 'ACTIVE'),
('沟通协作', '通用', '团队沟通与协作', 'ACTIVE'),
('问题解决', '通用', '问题分析与解决能力', 'ACTIVE'),
('代码审查', '通用', 'Code Review 代码审查', 'ACTIVE'),
('系统设计', '通用', '系统架构设计', 'ACTIVE'),
('设计模式', '通用', '软件设计模式', 'ACTIVE'),
('数据结构与算法', '通用', '数据结构与算法基础', 'ACTIVE');

-- ==================== 3. 职业角色（10 条） ====================

INSERT INTO occupation_role (name, description, category) VALUES
('后端开发工程师', '负责服务端业务逻辑开发、API 设计与数据库维护', '技术'),
('前端开发工程师', '负责 Web/移动端界面开发与用户体验优化', '技术'),
('测试工程师', '负责软件质量保障、自动化测试与性能测试', '技术'),
('运维工程师', '负责服务器部署、监控、CI/CD 流水线维护', '技术'),
('数据开发工程师', '负责数据平台建设、ETL 流程与数据治理', '技术'),
('算法工程师', '负责机器学习/深度学习模型研发与优化', '技术'),
('产品经理', '负责产品规划、需求分析与项目推进', '产品'),
('技术经理', '负责技术团队管理、技术选型与架构决策', '管理'),
('全栈开发工程师', '负责前后端全链路开发', '技术'),
('架构师', '负责系统架构设计、技术方案评审与性能优化', '技术');

-- ==================== 4. 职业角色技能关联（~60 条） ====================

-- 后端开发工程师（MUST: Java/Spring Boot/MySQL/Redis, NICE: Docker/Linux/Git, BONUS: Kafka/K8s）
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='后端开发工程师' AND s.name IN ('Java','Spring Boot','MySQL','Redis','SQL','RESTful API');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='后端开发工程师' AND s.name IN ('Docker','Linux','Git','Spring Cloud','MyBatis-Plus','Spring Security');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='后端开发工程师' AND s.name IN ('Kafka','Kubernetes','Elasticsearch','MongoDB');

-- 前端开发工程师
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='前端开发工程师' AND s.name IN ('JavaScript','TypeScript','Vue.js','HTML5','CSS3');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='前端开发工程师' AND s.name IN ('React','Webpack','Element Plus','Node.js','Axios');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='前端开发工程师' AND s.name IN ('ECharts','微信小程序','Sass/LESS','Pinia');

-- 测试工程师
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='测试工程师' AND s.name IN ('自动化测试','测试用例设计','Postman','缺陷管理');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='测试工程师' AND s.name IN ('Selenium','JMeter','CI/CD 测试','性能测试');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='测试工程师' AND s.name IN ('Appium','Cypress','Python','SQL');

-- 运维工程师
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='运维工程师' AND s.name IN ('Linux','Docker','Shell 脚本','Jenkins');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='运维工程师' AND s.name IN ('Kubernetes','Ansible','Prometheus','Grafana','Nginx');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='运维工程师' AND s.name IN ('Terraform','云服务（AWS/阿里云）','负载均衡');

-- 数据开发工程师
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='数据开发工程师' AND s.name IN ('Python','SQL','数据仓库','ETL');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='数据开发工程师' AND s.name IN ('Spark','Flink','Hadoop','Pandas');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='数据开发工程师' AND s.name IN ('数据分析','数据可视化','Kafka');

-- 算法工程师
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='算法工程师' AND s.name IN ('Python','机器学习','深度学习','数据结构与算法');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='算法工程师' AND s.name IN ('TensorFlow','PyTorch','NLP','Pandas','NumPy');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='算法工程师' AND s.name IN ('大语言模型','Spark','数据可视化');

-- 产品经理
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='产品经理' AND s.name IN ('需求分析','项目管理','沟通协作','数据分析');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='产品经理' AND s.name IN ('技术文档','敏捷开发','问题解决');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='产品经理' AND s.name IN ('系统设计','数据可视化');

-- 技术经理
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='技术经理' AND s.name IN ('系统设计','项目管理','代码审查','沟通协作');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='技术经理' AND s.name IN ('微服务架构','设计模式','敏捷开发','技术文档');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='技术经理' AND s.name IN ('Docker','Kubernetes','云服务（AWS/阿里云）');

-- 全栈开发工程师
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='全栈开发工程师' AND s.name IN ('Java','JavaScript','Vue.js','MySQL','Spring Boot');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='全栈开发工程师' AND s.name IN ('TypeScript','React','Redis','Docker','Git');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='全栈开发工程师' AND s.name IN ('Node.js','Linux','RESTful API');

-- 架构师
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'MUST'
FROM occupation_role r, skill s WHERE r.name='架构师' AND s.name IN ('系统设计','微服务架构','设计模式','Java');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'NICE'
FROM occupation_role r, skill s WHERE r.name='架构师' AND s.name IN ('Docker','Kubernetes','Spring Cloud','Redis','Kafka','Elasticsearch');
INSERT INTO occupation_role_skill (occupation_role_id, skill_id, requirement_level)
SELECT r.id, s.id, 'BONUS'
FROM occupation_role r, skill s WHERE r.name='架构师' AND s.name IN ('云服务（AWS/阿里云）','负载均衡','数据仓库');

-- ==================== 5. 技能同义词（20 条） ====================

INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'SpringBoot' FROM skill WHERE name = 'Spring Boot';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'Spring-Boot' FROM skill WHERE name = 'Spring Boot';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'spring boot' FROM skill WHERE name = 'Spring Boot';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'springboot' FROM skill WHERE name = 'Spring Boot';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'Vue' FROM skill WHERE name = 'Vue.js';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'vue3' FROM skill WHERE name = 'Vue.js';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'vuejs' FROM skill WHERE name = 'Vue.js';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'Mybatis' FROM skill WHERE name = 'MyBatis';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'mybatis-plus' FROM skill WHERE name = 'MyBatis-Plus';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'MBP' FROM skill WHERE name = 'MyBatis-Plus';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'pg' FROM skill WHERE name = 'PostgreSQL';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'postgres' FROM skill WHERE name = 'PostgreSQL';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'K8s' FROM skill WHERE name = 'Kubernetes';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'k8s' FROM skill WHERE name = 'Kubernetes';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'ES' FROM skill WHERE name = 'Elasticsearch';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'elastic' FROM skill WHERE name = 'Elasticsearch';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'JS' FROM skill WHERE name = 'JavaScript';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'TS' FROM skill WHERE name = 'TypeScript';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'react.js' FROM skill WHERE name = 'React';
INSERT INTO skill_synonym (skill_id, synonym)
SELECT id, 'reactjs' FROM skill WHERE name = 'React';

-- ==================== 6. 技能关系边（25 条） ====================

-- PREREQUISITE（前置依赖）
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.9
FROM skill s1, skill s2 WHERE s1.name='Java' AND s2.name='Spring Boot';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.8
FROM skill s1, skill s2 WHERE s1.name='Spring Boot' AND s2.name='Spring Cloud';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.8
FROM skill s1, skill s2 WHERE s1.name='HTML5' AND s2.name='Vue.js';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.7
FROM skill s1, skill s2 WHERE s1.name='JavaScript' AND s2.name='TypeScript';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.8
FROM skill s1, skill s2 WHERE s1.name='JavaScript' AND s2.name='Vue.js';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.7
FROM skill s1, skill s2 WHERE s1.name='Python' AND s2.name='机器学习';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.8
FROM skill s1, skill s2 WHERE s1.name='机器学习' AND s2.name='深度学习';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.6
FROM skill s1, skill s2 WHERE s1.name='Docker' AND s2.name='Kubernetes';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'PREREQUISITE', 0.7
FROM skill s1, skill s2 WHERE s1.name='Linux' AND s2.name='Shell 脚本';

-- SIMILAR（相似技能）
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.8
FROM skill s1, skill s2 WHERE s1.name='MyBatis' AND s2.name='MyBatis-Plus';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.7
FROM skill s1, skill s2 WHERE s1.name='Vue.js' AND s2.name='React';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.7
FROM skill s1, skill s2 WHERE s1.name='MySQL' AND s2.name='PostgreSQL';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.6
FROM skill s1, skill s2 WHERE s1.name='TensorFlow' AND s2.name='PyTorch';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.7
FROM skill s1, skill s2 WHERE s1.name='RabbitMQ' AND s2.name='Kafka';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.6
FROM skill s1, skill s2 WHERE s1.name='Webpack' AND s2.name='Vite';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.7
FROM skill s1, skill s2 WHERE s1.name='Maven' AND s2.name='Gradle';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.6
FROM skill s1, skill s2 WHERE s1.name='Jenkins' AND s2.name='GitLab CI';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'SIMILAR', 0.6
FROM skill s1, skill s2 WHERE s1.name='Prometheus' AND s2.name='Grafana';

-- INCLUDES（包含关系）
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'INCLUDES', 0.8
FROM skill s1, skill s2 WHERE s1.name='Spring Boot' AND s2.name='Spring MVC';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'INCLUDES', 0.7
FROM skill s1, skill s2 WHERE s1.name='Spring Boot' AND s2.name='Spring Security';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'INCLUDES', 0.6
FROM skill s1, skill s2 WHERE s1.name='微服务架构' AND s2.name='Spring Cloud';

-- COMPLEMENTARY（互补技能）
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'COMPLEMENTARY', 0.7
FROM skill s1, skill s2 WHERE s1.name='Java' AND s2.name='Redis';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'COMPLEMENTARY', 0.6
FROM skill s1, skill s2 WHERE s1.name='Docker' AND s2.name='Nginx';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'COMPLEMENTARY', 0.7
FROM skill s1, skill s2 WHERE s1.name='Python' AND s2.name='Pandas';
INSERT INTO skill_relation (skill_id, related_skill_id, relation_type, weight)
SELECT s1.id, s2.id, 'COMPLEMENTARY', 0.6
FROM skill s1, skill s2 WHERE s1.name='数据分析' AND s2.name='数据可视化';

