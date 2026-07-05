-- admin seed data (password: admin123, BCrypt)
INSERT INTO "user" (username, password, role, status)
VALUES ('admin', '$2a$10$iTqJbcM.EgZQnklereeHTexX9qo8rXX4z6cFjZGfmtlr6kCqXdg2i', 'ADMIN', 'NORMAL');