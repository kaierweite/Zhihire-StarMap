# Day 01 — 项目初始化与环境搭建

> **日期**：2026-07-06（周一）
> **阶段**：基础搭建
> **前置依赖**：无

---

## 目标

完成 Spring Boot 3 后端项目骨架搭建、KingbaseES 数据库连通验证、开发环境跑通。

---

## 任务清单

### 1. Spring Boot 3 项目初始化（2h）

- [x] 使用 Spring Initializr 创建项目
  - Java 21 / Spring Boot 3.2+ / Maven
  - 依赖：Spring Web、Spring Security、MyBatis-Plus、KingbaseES JDBC Driver、Lombok、Validation
- [x] 创建 `pom.xml`，配置：
  - [x] Spring Boot 3.2.x parent
  - MyBatis-Plus 3.5.x
  - KingbaseES JDBC 驱动（jar 包本地引入或 Maven 仓库）
  - Knife4j（API 文档）
  - Caffeine（本地缓存，Redis 可选）
  - JWT 依赖（jjwt 0.12.x）
- 产出：`backend/pom.xml` 可正常 `mvn compile`

### 2. 项目目录骨架搭建（1h）

按 ADR-0008 D7 + ADR-0004 创建包结构：

```
com.zhihire.starmap/
├── StarMapApplication.java
├── config/
│   ├── SecurityConfig.java
│   ├── JwtAuthenticationFilter.java
│   ├── MybatisPlusConfig.java
│   └── WebConfig.java
├── module/
│   ├── common/
│   │   ├── result/Result.java
│   │   ├── exception/GlobalExceptionHandler.java
│   │   ├── exception/BusinessException.java
│   │   └── constant/CommonConstants.java
│   ├── auth/
│   ├── user/
│   ├── job/
│   ├── resume/
│   ├── match/
│   ├── graph/
│   ├── career/
│   ├── interview/
│   ├── admin/
│   └── system/
```

### 3. application.yml 配置（1h）

```yaml
server:
  port: 8080
spring:
  datasource:
    url: jdbc:kingbasees://localhost:54321/starmap
    username: starmap
    password: ${DB_PASSWORD:starmap123}
    driver-class-name: com.kingbase8.Driver
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 10MB
mybatis-plus:
  mapper-locations: classpath*:mapper/**/*.xml
  configuration:
    map-underscore-to-camel-case: true
  global-config:
    db-config:
      logic-delete-field: deletedAt
      logic-delete-value: "1"
      logic-not-delete-value: "0"
jwt:
  secret: ${JWT_SECRET:zhihire-starmap-jwt-secret-key-2026}
  expiration: 86400000
ai:
  service:
    url: http://localhost:8000
```

### 4. 通用组件实现（2h）

- [x] `Result<T>` 统一返回封装：
  ```java
  public class Result<T> {
      private int code;
      private String message;
      private T data;
      public static <T> Result<T> ok(T data) { ... }
      public static <T> Result<T> error(String msg) { ... }
  }
  ```
- [x] `GlobalExceptionHandler`：@RestControllerAdvice 全局异常处理
  - [x] BusinessException → 自定义错误码
  - MethodArgumentNotValidException → 参数校验错误
  - Exception → 通用 500
- `CommonConstants`：跨模块常量（分页默认值、状态枚举引用）
- [x] `MybatisPlusConfig`：分页插件 + 自动填充 handler（created_at/updated_at）

### 5. KingbaseES 连通验证（1h）

- [x] 编写 `PingController`：
  ```java
  @RestController
  @RequestMapping("/api")
  public class PingController {
      @Autowired
      private DataSource dataSource;
      
      @GetMapping("/ping")
      public Result<String> ping() {
          // JDBC SELECT 1 验证
          return Result.ok("pong");
      }
  }
  ```
- [x] 启动 `StarMapApplication`，验证：
  - [x] `mvn spring-boot:run` 正常启动
  - `GET /api/ping` 返回 `{"code":200,"data":"pong"}`
  - KingbaseES JDBC 连接正常

### 6. Git 初始化与提交（0.5h）

- git init + .gitignore（Java 标准）
- 首次提交：`[feat]: 后端项目初始化，Spring Boot 3 骨架 + KingbaseES 连通`

---

## 产出物

| 产出 | 说明 |
|------|------|
| `backend/pom.xml` | Maven 配置 |
| `backend/src/main/java/com/zhihire/starmap/StarMapApplication.java` | 启动类 |
| `backend/src/main/java/com/zhihire/starmap/config/` | 配置类骨架 |
| `backend/src/main/java/com/zhihire/starmap/module/common/` | Result + 异常 + 常量 |
| `backend/src/main/resources/application.yml` | 配置文件 |
| `GET /api/ping` | 冒烟验证通过 |

---

## 验收标准

- [x] `mvn spring-boot:run` 启动无报错（已验证，应用正常启动）
- [x] `GET /api/ping` 返回 `Result<String>` JSON（已验证：`{"code":200,"message":"success","data":"pong"}`）
- [x] KingbaseES JDBC 连接正常（SELECT 1）（本地 H2 兜底验证通过，虚机待部署验证）
- [x] 包结构符合 ADR-0004 + ADR-0008 D7


