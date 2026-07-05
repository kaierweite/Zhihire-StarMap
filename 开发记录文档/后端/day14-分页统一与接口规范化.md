# Day 14 — 分页统一 + 接口规范化

> **日期**：2026-07-19（周日）
> **阶段**：质量保障
> **前置依赖**：Day 13（所有业务模块）

---

## 目标

统一分页约定、接口规范化、全局异常完善。

---

## 任务清单

### 1. 分页统一（1.5h）

- [x] 确保所有 list 接口走分页：
  - [x] 参数：page(默认1) + size(默认20, 最大100)
  - [x] MyBatis-Plus Page<T>
  - Result<T> 分页返回：`{records, total, page, size}`
- [x] 检查并修复所有 list 接口：
  - [x] user/list, job/list, resume/list, skill/list
  - recommend/jobs, recommend/talents
  - admin/user/list, admin/company/list, admin/logs
  - notification/list, interview/list

### 2. 接口路径规范化（1h）

- 确保所有接口前缀 `/api/`
- RESTful 风格：GET 查询 / POST 创建 / PUT 更新 / DELETE 删除
- [x] 统一参数校验：@Valid + @NotBlank / @NotNull

### 3. 全局异常完善（1h）

- [x] 补充业务异常：
  - UserNotFoundException
  - JobNotFoundException
  - ResumeNotFoundException
  - UnauthorizedException（未登录访问受保护接口）
  - ForbiddenException（权限不足）
  - FileUploadException（文件校验失败）
  - AI service 调用失败 → 重试 + 降级提示
- 每个异常映射到 HTTP 状态码 + 业务错误码

### 4. Knife4j API 文档（0.5h）

- 配置 Knife4j（Swagger UI）
- 为所有 Controller 添加 @Tag + @Operation 注解
- 验证 `http://localhost:8080/doc.html` 可访问

---

## 产出物

| 产出 | 说明 |
|------|------|
| 统一分页 | 所有 list 接口 page + size |
| 异常体系 | 完整业务异常 + HTTP 映射 |
| Knife4j | API 文档可访问 |

---

## 验收标准

- [x] 所有 list 接口支持 page + size 分页
- [x] 超 500 条只返前 500 + 提示
- [x] 异常返回统一格式 {code, message, data}
- [x] Knife4j 文档页可访问
