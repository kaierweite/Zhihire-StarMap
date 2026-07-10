# 状态字段一律 VARCHAR 语义化枚举

所有业务状态与角色字段统一用 VARCHAR 存大写语义常量（角色 ADMIN/USER/COMPANY；状态 NORMAL/DISABLED/BANNED 等），并以此贯穿数据库、Python 模型、JWT claim 与 FastAPI 鉴权依赖。废弃 `setStatus(1)`/`getStatus()==0` 的 INT 写法与 `.hasRole("admin")` 的小写写法——后两者会让 JWT 大写 claim 与小写角色匹配不上，鉴权静默失效。

之所以不用更"省空间"的 INT 状态，是因为赛题文档（AGENTS.md、day02）已明确要求 VARCHAR 语义化枚举，且比赛演示中手翻数据库/查日志时枚举字面量远比 0/1 可读；一致的大写还能让前端配置开关、Python 常量、SQL 字面量三者天然对齐，省掉一层映射。代价是统一改写示例代码，远小于让 FastAPI 鉴权在演示前夜跑不通的代价。
