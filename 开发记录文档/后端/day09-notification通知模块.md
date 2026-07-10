# Day 09 — Notification 通知模块

> **前置依赖**：day01 auth
> **前端对应**：UserNotifications.vue / CompanyNotifications.vue / AppHeader.vue（红点）
> **核心 ADR**：ADR-0010 + V4 Q16/Q18

---

## 目标

通知列表、未读计数、标记已读。前端每 30s 轮询未读数。

---

## 涉及数据表

- `notification` — 通知表（user_id, type, title, content, is_read, is_deleted, created_at）

---

## API 清单

### 1. GET `/api/notification`

- 当前用户通知列表
| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | INTERVIEW_INVITE / APPLICATION / SYSTEM |
| page/size | int | 分页 |

- 软删除过滤
- 返回 `Result<PageData<NotificationVO>>`

### 2. GET `/api/notification/unread-count`

- 前端每 30s 轮询
- 返回 `Result<{ count }>`

### 3. PUT `/api/notification/{id}/read`

- 标记单条已读
- 返回 `Result[null]`

### 4. PUT `/api/notification/read-all`

- 标记全部已读
- 返回 `Result[null]`

---

## 通知触发点

| 触发动作 | 通知对象 | type |
|----------|---------|------|
| 求职者投递岗位 | 企业HR | APPLICATION |
| 企业发起面试邀请 | 求职者 | INTERVIEW_INVITE |
| 系统消息 | 全体/单用户 | SYSTEM |

- 清理：保留近 30 天 + 自动软删超期行

---

## 代码分层

| 层 | 文件 |
|----|------|
| 路由 | `api/v1/notification.py` |
| 服务 | `services/notification_service.py` |
| 仓储 | `repositories/notification_repository.py` |

---

## 验收标准

- [ ] 投递/邀请 → 通知自动生成
- [ ] 未读数轮询正确
- [ ] 标记已读 → 未读数减少
- [ ] 全部已读 → 计数归零
