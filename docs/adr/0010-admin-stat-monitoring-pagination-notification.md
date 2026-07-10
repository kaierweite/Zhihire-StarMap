# ADR-0010: 后台统计、监控、操作日志、数据维护、分页与 notification 口径

**日期**：2026-07-01
**状态**：已采纳
**关联**：V4 决策记录 Q10 / Q17 / Q18

## 背景

赛题功能 5「平台管理与监控后台」要求用户管理、数据维护等操作。V2 22 表有 `operation_log` / `notification` 表但无落点口径；列表接口无分页约定；`notification` 无已读状态与清理口径。

## 决策

### 一、后台统计

- 后台统计用 SQL 实时聚合 + aiocache 短缓存（5 分钟）。
- `StatService` 用 SQL `COUNT` 统计用户 / 岗位 / 匹配 / 解析。
- 接口 `GET /api/admin/stat` 返回 `{userCount, companyCount, jobCount, matchCount, parseCount}`。
- 不开统计汇总表（不值），用实时聚合。

### 二、监控

- 监控窄化为 service 状态卡片：`/ai/health` + `/api/ping` + KingbaseES `SELECT 1`，管理端首页三绿点条。
- 不开 Prometheus / Grafana（四核 8GB 跑不起）。

### 三、操作日志

- `operation_log` 用 FastAPI 中间件/装饰器 `@operation_log("模块/动作")` 拦截落库。
- 演示前 `@operation_log` 装饰器覆盖登录、岗位发布、字典审核、推荐触发，日志页有数据可放。

### 四、数据维护

- 显式落两条：
  - 「管理员后台·岗位下架」——强制下架违规岗位（`job.status = CLOSED`）。
  - 「用户封禁」——`user.status = BANNED`。
- 演示叙事镜 7 加「管理员可介入下架违规岗位、封禁违规用户」。

### 五、分页约定

- 统一分页参数 `page + size`，默认 `size = 20`，`size ≤ 100`。
- 所有 list 接口走分页，SQLAlchemy `offset/limit` + `select(func.count())` 计总数。
- `Result<T>` 分页返回 `{records, total, page, size}` 约定。
- 前端 Element Plus `el-pagination` 或 loadMore。
- 推荐列表分页基于已缓存 `match_result`，「看更多」翻页不重调 AI（与 V4 Q1 一致）。
- 总量兜底：岗位 / 候选人列表超 500 时只返前 500 + 提示「结果过多，请增加筛选」，不强求全量排序。

### 六、notification

- `notification` 加 `is_read BOOLEAN`（默认 false）+ `type VARCHAR`（`APPLICATION` / `INTERVIEW_INVITE` / `SYSTEM`）。
- 已读由用户点通知或进通知页触发 `PUT /api/notification/{id}/read`；红点 = `is_read = false` 计数。
- 前端轮询未读数：`GET /api/notification/unread-count` 每 30s 拉一次，右上角铃铛显示。
- 清理：保留近 30 天 + 自动软删（`deleted_at`）超期行，写进 `install.sh` 定时任务。

## Considered Options

- **A 实时聚合 + 装饰器日志 + 轻量监控（采纳）**：8GB 跑不起重型监控栈，SQL 聚合够用。
- **B 统计汇总表 + Prometheus**：不值且装不上。
- **C 无操作日志无分页**：演示无数据、列表卡死。

## Consequences

- 后端实现 `StatService`、`@operation_log` 装饰器、分页 `Result[T]` 约定。
- `notification` 表加 `is_read` + `type` 字段。
- `install.sh` 加 notification TTL 定时任务。
- 前端加未读轮询、分页组件、加载态统一。
