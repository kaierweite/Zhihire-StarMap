# ADR-0008: 启动开发 grilling V3 收口决策

**日期**：2026-06-30
**状态**：已采纳
**关联**：V2决策记录、ADR-0001 / 0003 / 0005 / 0007

## 背景

需求与设计阶段（V2 grilling 收口 + 七个 ADR）已完成，现进入代码落地启动。
本轮对「启动开发」进行 grilling，解决 Figaro 落地前的可逆性中等决策：
注释尺度、冒烟时机、仓库组织、表结构审计、后端包结构。

本次未推翻任何 V2 决策，全部 V2 决策有效；本 ADR 仅补充落地口径。

## 决策

### D1 逐行中文注释尺度
采用「逐逻辑语句 + 逐函数/类 docstring」中文注释：
- 每个有意义的语句/语句块挂一行中文说明，说清 Why 与作用
- 每个函数/方法/类挂中文 docstring（职责 / 入参 / 出参 / 异常）
- 不对空行、括号行、import 行强行挂注释
- 代码标识符保持英文
- 废话注释（如 `# i 加 1`）禁止

### D2 开发流水线
Windows 开发 → 提交 GitHub → 麒麟虚机 git pull 运行。
虚机已到手（账号密码已交组长）。

### D3 冒烟关卡前置
将「day3 前麒麟冒烟必须过」前推为 day1 并行动作。
先打三端最小冒烟骨架（FastAPI `/api/ping`、
FastAPI `/ai/health`、KingbaseES `SELECT 1`），
推 GitHub 在虚机拉起验证 LoongArch + Kylin + KingbaseES 真能跑。
目标：把最可能翻车的环境依赖（docling 无 loongarch64 wheel、
KingbaseES 驱动、asyncpg、Python 3.12 loongarch 可得性）
在最早暴露，避免 day19 才发现关键依赖装不上。

### D4 冒烟代码落点
冒烟骨架直接落在正式骨架根目录 `backend/app`，
不建 `smoke/` 一次性目录。冒烟用骨架即正式骨架，
通过后在此骨架上直接长出业务模块，不返工。

### D5 数据库建表粒度
22 表一次性全量建齐，拆三个文件按依赖分层：
- `01_schema.sql`：22 张 `CREATE TABLE`；
  自引用/环外键用 `DEFERRABLE INITIALLY DEFERRED`
  或后置 `ALTER TABLE ADD CONSTRAINT`
- `02_index.sql`：唯一索引与查询索引
- `03_seed.sql`：种子数据（`role`、`admin` 账号、若干 ACTIVE 技能、
  `skill_relation` 示例边）

### D6 表结构审计结果
对 V1 19 表按 V2 决策审计，变更正负相抵后维持 22 表口径：
- 删 `interview_question`（V2 Q5 删面试助手）
- 新增 `skill_relation` / `role` / `role_skill` / `skill_synonym`（V2 Q2 / Q3）
- `skill` 加 `status` / `merge_target_id`，补 `updated_at` / `deleted_at`
- `user_profile` 加 `current_city`（V2 Q4 居住城市加分）
- 删 `match_result.reason`，并入 `match_detail.rationale`（V2 Q4 契约）
- `resume` 去掉文件字段，改为 `file_id` FK → `upload_file.id`（单一事实源）
- 日志类 append-only 表补 `deleted_at`，不补 `updated_at`（口径豁免）

最终 22 表：`user` / `user_profile` / `company` / `resume` / `job` / `skill` /
`user_skill` / `job_skill` / `match_result` / `recommend_record` / `career_plan` /
`login_log` / `operation_log` / `notification` / `upload_file` / `parse_task` /
`ability_graph` / `ai_chat_history` / `skill_relation` / `role` / `role_skill` /
`skill_synonym`

### D7 后端包结构
按业务域 module 切，每个 module 内再分层：
`app/api/v1/{auth,user,job,resume,match,graph,career,interview,notification,company,admin}.py` + `app/services/` + `app/repositories/`
`app/core/`（算法）+ `app/models/{entities,schemas,enums}`。
仓储统一在 `app/repositories/`，路由在 `app/api/v1/` 聚合。
`Result<T>`、全局异常、JWT 过滤器住在 `module.common` 或顶层 `config/`。

### D8 KingbaseES 虚机待验证
虚机已到手，KingbaseES 连通性明天白天实测（未验证）：
- 已装可连 → 冒烟脚本直连真库，day1 全程跑通
- 已装未初始化 → day1 先 `initdb` + 建用户 + 建库再冒烟
- 未装 → day1 需含 KingbaseES 安装 + 授权 + 初始化，冒烟脚本内置兜底

## 后果

- 21 天版为唯一执行计划，30 天版降级参考
  （已在 `docs/项目开发计划.md` 顶部标注）
- 三份旧时序图按 V2 对齐重写，旧版降级引用标记
  （各文件顶部加「V1 废弃」声明，保留正文备查）
- 新增 `docs/提交清单.md` 为八项交付物单一事实源
- 新增 `deploy/` 三件套骨架：`README`、`部署架构.md`、`依赖可得性清单.md`
- 新增 `database/README.md` 记录 22 表审计结果与建表计划
- `CONTEXT.md` 补「逐行中文注释」术语、刷新当前状态与风险表
