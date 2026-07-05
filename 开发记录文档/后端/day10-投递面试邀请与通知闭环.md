# Day 10 — 投递/面试邀请 + 通知闭环

> **日期**：2026-07-15（周三）
> **阶段**：核心业务（三）
> **前置依赖**：Day 09（匹配推荐）

---

## 目标

完成求职者投递、企业面试邀请、通知闭环全链路。

---

## 任务清单

### 1. RecommendRecord 实体（0.5h）

- [x] `RecommendRecord` 实体：id, resumeId, jobId, recommendType(JOB/TALENT), isClicked, isApplied, isInvited, createdAt

### 2. 投递接口（1h）

- [x] `POST /api/recommend/job/{jobId}/apply` — 求职者投递岗位
  - 更新 recommend_record.is_applied = true
  - 给企业发 notification（type=APPLICATION, resumeId, jobId）
- `PUT /api/recommend/record/{id}/click` — 点击记录（is_clicked=true）

### 3. 面试邀请接口（1h）

- `POST /api/recommend/talent/{resumeId}/invite` — 企业发起面试邀请
  - 更新 recommend_record.is_invited = true
  - 给求职者发 notification（type=INTERVIEW_INVITE, jobId, resumeId）
- `GET /api/recommend/invitations` — 查看收到的面试邀请

### 4. 通知模块（1.5h）

- `Notification` 实体：id, userId, type(APPLICATION/INTERVIEW_INVITE/SYSTEM), title, content, isRead, relatedId, createdAt
- [x] 接口：
  - `GET /api/notification/list` — 通知列表（分页，按 created_at DESC）
  - `GET /api/notification/unread-count` — 未读数
  - `PUT /api/notification/{id}/read` — 标记已读
  - `PUT /api/notification/read-all` — 全部已读

---

## 产出物

| 产出 | 说明 |
|------|------|
| `module/match/entity/RecommendRecord.java` | 推荐记录实体 |
| `module/system/entity/Notification.java` | 通知实体 |
| `POST /api/recommend/job/{jobId}/apply` | 投递接口 |
| `POST /api/recommend/talent/{resumeId}/invite` | 面试邀请接口 |
| `GET /api/notification/unread-count` | 未读通知数 |

---

## 验收标准

- [x] 投递后 recommend_record.is_applied = true
- [x] 投递后给企业发 notification(type=APPLICATION)
- [x] 面试邀请后 recommend_record.is_invited = true
- [x] 面试邀请后给求职者发 notification(type=INTERVIEW_INVITE)
- [x] 未读通知数接口正确返回
- [x] 标记已读后 is_read = true
