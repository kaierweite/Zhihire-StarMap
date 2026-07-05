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