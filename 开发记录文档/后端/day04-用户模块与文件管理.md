# Day 04 — 用户模块 + 文件管理

> **日期**：2026-07-09（周四）
> **阶段**：核心业务（一）
> **前置依赖**：Day 03（鉴权）

---

## 目标

完成用户档案 CRUD、文件上传（10MB + 双层校验 + 单一事实源）。

---

## 任务清单

### 1. User 模块 CRUD（1.5h）

- [x] `UserProfile` 实体：userId, currentCity, education, experience, profileCompleteness, skills(JSONB), embeddingCache(JSONB)
- [x] `Company` 实体：id, userId, name, industry, auditStatus(UNVERIFIED/PENDING/VERIFIED/REJECTED), auditReason
- [x] 接口：
  - [x] `GET /api/user/profile` — 获取当前用户档案（需认证）
  - `PUT /api/user/profile` — 更新档案
  - `GET /api/company/profile` — 获取企业档案
  - `PUT /api/company/profile` — 更新企业信息

### 2. 文件上传模块（2.5h）

- `UploadFile` 实体：id, originalName, storagePath, fileSize, fileType, mimeType, createdAt
- [x] 文件存储路径：`/data/starmap/files/{yyyy-mm}/{uuid}.{ext}`
- [x] `SystemFileService`：
  - [x] 校验文件大小 ≤ 10MB
  - 校验扩展名白名单（.pdf/.doc/.docx）
  - 魔数校验（%PDF / DOCX ZIP 头）
  - 生成 UUID 文件名，写入磁盘
  - 写入 upload_file 表
- `module.resume.controller.ResumeController`：
  - `POST /api/resume/upload` — 上传简历文件
    - 接收 MultipartFile
    - 调 SystemFileService 存储
    - 创建 resume 记录（file_id 引用 upload_file）
    - 创建 parse_task 记录（status=WAITING）
    - 返回 parse_task.id（异步解析将由 AI 服务处理）
  - `GET /api/resume/list` — 当前用户简历列表（分页）
  - `GET /api/resume/{id}` — 简历详情

### 3. ParseTask 轮询接口（0.5h）

- `GET /api/parse/task/{id}` — 查询解析任务状态
  - 返回 parse_task 的 status + parsedData（如已完成）
  - status: WAITING / PARSING / SUCCESS / FAILED / REJECTED

### 4. 异步解析触发（0.5h）

- `@Async` 方法调用 AI 服务 `/ai/parse/resume`
- 用 `@Async` + `CompletableFuture` 异步执行
- AI 服务返回后更新 parse_task.status + resume.parsed_data

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/user/` | UserProfile + Company CRUD |
| `module/resume/` | 简历上传 + 文件管理 |
| `module/system/` | SystemFileService（文件存储） |
| `POST /api/resume/upload` | 文件上传接口（10MB + 双层校验） |
| `GET /api/parse/task/{id}` | 解析状态轮询接口 |

---

## 验收标准

- [x] 文件上传 10MB 限制生效
- [x] 扩展名白名单 + 魔数校验生效
- [x] 文件存储路径正确（/data/starmap/files/{yyyy-mm}/）
- [x] upload_file 单一事实源，resume 通过 file_id 引用
- [x] parse_task 创建成功，状态 WAITING
- [x] 异步解析触发链路打通

