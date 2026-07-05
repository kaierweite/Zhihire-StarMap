# 智聘星图后端（Spring Boot 3 主服务）

> 冒烟骨架待启动。详见 `docs/开发流程时序图.md` day1-2。

## 目录说明

```
backend/
├── src/
│   ├── main/
│   │   ├── java/com/zhihire/starmap/
│   │   │   ├── StarMapApplication.java    # 启动类
│   │   │   ├── config/                    # JWT 过滤器、Spring Security 配置
│   │   │   └── module/                    # 按业务域 module 切（ADR-0008 D7）
│   │   │       ├── common/                # Result<T>、全局异常、常量
│   │   │       ├── auth/                  # 认证
│   │   │       ├── user/                  # 用户
│   │   │       ├── job/                   # 岗位
│   │   │       ├── resume/                # 简历
│   │   │       ├── match/                 # 匹配
│   │   │       ├── graph/                 # 图谱
│   │   │       ├── career/                # 职业规划
│   │   │       │   ├── controller/
│   │   │       │   ├── service/
│   │   │       │   ├── mapper/
│   │   │       │   ├── entity/
│   │   │       │   └── dto/
│   │   │       ├── interview/             # 面试：模拟面试/报告/题库/简历优化（ADR-0011）
│   │   │       │   ├── controller/
│   │   │       │   ├── service/
│   │   │       │   ├── mapper/
│   │   │       │   ├── entity/
│   │   │       │   └── dto/
│   │   │       ├── admin/                 # 后台
│   │   │       └── system/                # 系统
│   │   └── resources/
│   │       ├── application.yml
│   │       └── mapper/
│   └── test/
└── pom.xml
```

## 技术栈

- Spring Boot 3 + MyBatis-Plus + JWT + Redis（可选 Caffeine 兜底）
- KingbaseES（国产数据库）
