-- admin seed data (password: admin123, BCrypt)
INSERT INTO "user" (username, password, role, status)
VALUES ('admin', '$2a$10$4Bc2m1tCycQs00D3qibHfuMTI8J1G4CceQWzQND6911e0Evsf8/ne', 'ADMIN', 'NORMAL');

-- skill seed data
INSERT INTO skill (name, category, status) VALUES ('Java', '后端', 'ACTIVE');
INSERT INTO skill (name, category, status) VALUES ('Spring Boot', '后端', 'ACTIVE');
INSERT INTO skill (name, category, status) VALUES ('Vue.js', '前端', 'ACTIVE');
INSERT INTO skill (name, category, status) VALUES ('Python', '数据', 'ACTIVE');
INSERT INTO skill (name, category, status) VALUES ('Docker', '运维', 'ACTIVE');
INSERT INTO skill (name, category, status) VALUES ('Kubernetes', '运维', 'CANDIDATE');

-- synonym seed data
INSERT INTO skill_synonym (skill_id, synonym) VALUES (1, 'Java8');
INSERT INTO skill_synonym (skill_id, synonym) VALUES (2, 'SpringBoot');
INSERT INTO skill_synonym (skill_id, synonym) VALUES (2, 'Spring-Boot');
INSERT INTO skill_synonym (skill_id, synonym) VALUES (3, 'Vue');
INSERT INTO skill_synonym (skill_id, synonym) VALUES (5, 'K8s');
-- occupation_role seed data
INSERT INTO occupation_role (name, description, category) VALUES ('后端开发工程师', '服务端业务逻辑开发', '技术');
INSERT INTO occupation_role (name, description, category) VALUES ('前端开发工程师', 'Web 界面开发', '技术');
INSERT INTO occupation_role (name, description, category) VALUES ('测试工程师', '软件质量保障', '技术');
INSERT INTO occupation_role (name, description, category) VALUES ('产品经理', '产品规划与需求分析', '产品');