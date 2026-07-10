# 后端包名与核心实体命名

后端 Python 代码统一置于 `app`（与 AGENTS.md 项目规范一致），分层为 `app/{api, services, core, infrastructure, models, repositories, config, db}`，路由在 `app/api/v1/` 聚合，启动入口 `app/main.py`。核心业务实体去前缀，与 day02 表名一一对应：User / UserProfile / Company，废弃示例中的 SysUser / SysCompany。

day03 写的 `com.zhihire`（无 starmap）和 day04 的 SysUser 都不采用。前者与 AGENTS.md 主规范不符；Sys 前缀在本设计里没有"系统用户 vs 业务用户"的区分依据，day02 已把表名定为 user 而非 sys_user，实体跟表名走最清晰。越晚改 import 越痛，故在动代码前钉死。