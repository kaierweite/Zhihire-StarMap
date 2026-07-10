# 上下文记录 — 智聘星图 (Zhihire StarMap)

> 使用此文件记录开发中的重要上下文信息，供 AI 和团队成员快速了解当前状态。
> 口径以 `docs/V4决策记录.md`、`docs/adr/`（0001-0011）与 `docs/提交清单.md` 为准；本文与之冲突处以 V4 / ADR 为准。

## 项目简述

智聘星图是一个基于 AI、大模型和知识图谱技术的人才智能招聘平台，部署于银河麒麟操作系统（LoongArch 架构）上，使用人大金仓 KingbaseES 数据库。AI 算力全走云端大模型 API（DeepSeek），不在演示机本地加载大模型。AI 能力（文档解析 / 知识图谱 / 推荐算法）全部内置于 FastAPI 主服务，不再独立部署。

## 当前状态

（以 V4 grilling 22 条决策 + ADR 0001-0011 为准，最近回看：2026-07-06）

### ✅ 已完成
- [x] 赛题分析与需求拆解
- [x] 技术选型与架构设计
- [x] 功能模块图、业务流程图、用例图
- [x] 原型页面清单（common/user/company/admin 共 21 个页面）
- [x] 原型页面清单（common/user/company/admin 共 22 个页面；V4 后新增 user 端「个人中心」页承载 REQ-022 个人档案管理）
- [x] 数据库 ER 设计（22 张表）
- [x] 项目开发计划（21 天版为唯一执行计划，30 天版已降级参考）
- [x] 项目目录结构定义（V4 对齐版，按业务域切分）
- [x] V4 grilling 22 条决策收口（`docs/V4决策记录.md`）
- [x] ADR 0001-0011 全部落地
- [x] 演示叙事分镜（`docs/演示叙事.md`，PPT 与视频同源）
- [x] 三份时序图 V4 对齐版（开发流程 / 系统交互 / 系统架构）
- [x] `docs/提交清单.md` 八项交付物单一事实源
- [x] `deploy/` 骨架：README + 部署架构.md + 依赖可得性清单.md
- [x] `database/README.md` 记录 22 表审计结果与建表计划

### ❌ 未开始（待启动）
- [ ] 原型图重画（21 页，drawio 占位已备好，待绘制）
- [ ] 后端冒烟骨架（FastAPI `/api/ping` + KingbaseES `SELECT 1`）
- [ ] **麒麟虚机冒烟关卡**（day1-2 推上 GitHub 在虚机拉起验证三件套）
- [ ] 数据库建表脚本（`01_schema.sql` / `02_index.sql` / `03_seed.sql`，按 V4 22 表）
- [ ] 后端 FastAPI 业务模块（含 AI 能力，按 `app/{模块}/` 切）
- [ ] 前端 Vue 3 项目代码
- [ ] 需求分析文档 V2（按 V4 口径重写）
- [ ] 设计文档 / 产品说明书 / 测试报告
- [ ] 部署脚本 `install.sh` + 部署文档（裸部署 systemd 为主，见 ADR-0007）
- [ ] 演示 PPT / 演示视频（按 `docs/演示叙事.md` 同源分镜）

## 开发计划亮点

- 21 天版为唯一执行计划：第 14 天核心功能、第 18 天全部功能、第 21 天答辩材料
- day1-2 冒烟前推（ADR-0008 D3）：前后端双端最小骨架先在麒麟虚机拉起探雷，未过不进业务
- day7/8/12/13/14 按 V4 重写（删 PDFBox/Ollama、加图谱本体、改可解释子分、删薪资预测）
- 目标：二等奖保底，冲击一等奖

## 已知风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| 龙芯环境不兼容 | 高 | day1-2 麒麟虚机冒烟关卡 + loongarch64 依赖可得性清单 + 裸部署优先（ADR-0007/0008） |
| AI 解析准确率不足 | 中 | 预置提示词模板 + 技能字典审核页人工修正 + 字典三态兜底（ADR-0003） |
| 大模型 API 不稳定 | 中 | 增加重试机制 + 配置项指向备用云端 endpoint（ADR-0001） |
| KingbaseES 虚机未装/未初始化 | 中 | day1 先 initdb + 建用户 + 建库再冒烟（ADR-0008 D8） |
| 需依赖装不上（如 numpy/sklearn on loongarch64） | 中 | 脱依赖优先于 Docker 打包；启动脚本装不上即 `exit 1`（ADR-0007） |
| 8GB 内存紧张 | 中 | 内存预算待实测；aiocache 默认内存缓存兜底（JWT 黑名单 + 验证码 + 统计缓存），不做 DB 层数据缓存（ADR-0007/V4 Q20） |

---

## 语言 (Ubiquitous Language)

> 本节记录项目中已敲定的核心术语，作为 AI 与团队共享词典。仅收项目特有概念，不含通用编程术语。

**逐行中文注释 (Line-level Chinese Comments)**：
本仓代码注释采用「逐逻辑语句 + 逐函数/类 docstring」中文注释尺度：每个有意义的语句/语句块挂一行中文说明（说清 Why 与作用），每个函数/方法/类挂中文 docstring（职责/入参/出参/异常），不对空行、括号行、import 行强行挂注释，代码标识符保持英文，废话注释（如 `# i 加 1`）禁止。_避免_：逐物理行注释（含括号/空行）、全英文注释、废话注释。

详见 ADR-0008 D1。

**AI 调用模式 (AI Invocation Model)**：
系统 AI 算力**全走云端**大模型 API（DeepSeek 为主，可挂备用云厂商）。简历解析、岗位解析、职业规划、推荐打分四条链路统一走云端。模型「可切换」不做成用户可见的本地/云端开关，而是体现为**配置项指向不同云端 endpoint / API Key**。不在演示机本地加载大模型（Ollama/Qwen2.5 已废弃）。embedding 不走本地 sentence-transformers（依赖 PyTorch，被 LoongArch 硬约束排除），用云端接口或退路 BM25/TF-IDF。embedding 落库缓存（resume/job 加 `embedding_cache JSONB`），仅解析/编辑时由主服务算一次写回，推荐时取缓存向量求余弦，不再每次请求打云端。_避免_：本地大模型、HR 可见模型开关、sentence-transformers。

详见 ADR-0001。

**状态 (Status)**：
所有业务状态字段统一使用 VARCHAR 语义化枚举常量，全大写。角色 ADMIN/USER/COMPANY；账户与记录状态 NORMAL/DISABLED/BANNED（岗位 OPEN/CLOSED/DRAFT、简历解析 WAITING/PARSING/SUCCESS/FAILED/REJECTED 等同此风格）。技能字典三态 ACTIVE/CANDIDATE/MERGED。企业审核 UNVERIFIED/PENDING/VERIFIED/REJECTED。JWT claim 写大写，FastAPI 通过 `Depends(get_current_user)` + `python-jose` 解析。_避免_：INT 数字状态（0/1）、小写角色名、setStatus(1) 式用法。

详见 ADR-0002。

**文档解析 (Document Parsing)**：
PDF/DOC/DOCX 的文本抽取与结构化统一在 FastAPI 主服务内完成（pdfplumber + python-docx），产出 `raw_text` 与结构化 JSON。解析采用**异步 + 前端轮询**：后端用 `BackgroundTasks` 或 `asyncio.create_task` 异步调 AI，HTTP 立即返 `parse_task.id`；前端轮询 `GET /api/parse/task/{id}`（间隔 2s，超 30s 提示「稍后在简历列表看结果」），不用 SSE/WebSocket。parse_task.status = FAILED 时前端简历项标红 + 「重新解析」按钮。文件上传大小上限 10MB，类型校验双层（扩展名白名单 + 魔数校验），伪文件即拒（`parse_task.status = REJECTED`）。存储路径 `/data/starmap/files/{yyyy-mm}/`，文件名 UUID。_避免_：SSE/WebSocket 轮询、50MB 上限、无类型校验。

详见 ADR-0003、V4 Q3/Q12。

**后端分层架构 (Backend Layered Architecture)**：
后端代码统一置于 `backend/app/`。分层：`api/`（路由层，只做参数校验和响应封装）→ `services/`（业务服务层，编排 core + infrastructure）→ `core/`（核心算法层，无外部依赖：解析/归一/图谱/匹配/职业规划）→ `infrastructure/`（基础设施层，外部依赖防腐：LLM / 缓存 / 文件存储）→ `models/`（Pydantic 模型 + SQLAlchemy ORM + 枚举）→ `repositories/`（仓储层，只做原子数据库操作）。启动入口 `app/main.py`，启动命令 `uvicorn app.main:app --reload`。`Result[T]` Pydantic 模型、全局异常、跨模块常量住在 `services/` 或 `config/`；JWT 过滤器放 `api/deps.py`（横向关切）。models 内 `entities/`（ORM）、`schemas/`（Pydantic）、`enums/`（枚举）三子包，module 内不共享 dto。_避免_：按层切包（controller/service/mapper 平铺）、路由层混放业务逻辑。

详见 ADR-0004、ADR-0008 D7、V4 Q8。

**核心实体命名 (Core Entities)**：
核心业务实体去前缀，与表名一一对应：User / UserProfile / Company。_避免_：SysUser / SysCompany 等 Sys 前缀。

详见 ADR-0004。

**技能归一 (Skill Normalization)**：
从 AI 解析出的自然语言技能到 `user_skill`/`job_skill` 里的 `skill_id`，由 AI 出归一名、后端查表兜底。「AI 输出 `{raw, canonical_name, confidence}`；后端按 `canonical_name` 唯一索引查字典，查不到则建 `skill.status = CANDIDATE`；待人工校准转 `ACTIVE` 才上图谱边」。`skill_synonym` 同义表 + `merge_target_id` 管理合并。归一名走 skill + synonym 双查兜底：命中 synonym 取其 `merge_target` 对应 ACTIVE 行，未命中才建 CANDIDATE。同义兜底从「事后」提到「入库当场」。`skill` 表带 `category` 字段（后端/前端/测试/运维/数据/通用），前端按 category 上色，community detection 兜底有 category 作证。后台「技能字典审核页」是人工修正落点。_避免_：AI 直出 skill_id 并可造新、后端裸拿 raw_text 入库、同义只事后查。

详见 ADR-0003、V4 Q4/Q21。

**能力图谱本体 (Ability Graph Ontology)**：
图谱不是 ECharts 关系图 + 关联表，是轻量级知识图谱。`skill_relation` 表带四类语义边（PREREQUISITE / INCLUDES / SIMILAR / COMPLEMENTARY）+ weight；`skill` 自引用层级收进 `INCLUDES` 边。`occupation_role`（职业角色，V4 Q11 从 `role` 重命名）+ `occupation_role_skill`（`requirement_level` MUST/NICE/BONUS）支撑职业路径推荐。`job` 加 `occupation_role_id` 挂联职业角色。图谱权威在主服务**内存中的 networkx 图对象**（技能字典规模小，常驻够用）；`ability_graph` 表只缓存渲染用 ECharts payload，DB 不是图谱本身。主服务启动时（lifespan 钩子）从 DB 全量重建 networkx 图；uvicorn `--workers 1` 写死，内存图单份；字典审核改 `skill.status` 或 `skill_relation` 后调 `POST /api/graph/reload` 全量重建。SIMILAR 边预置口径：同 category 内高频技能两两建 SIMILAR 边（weight 默认 0.5），跨 category 建少量 COMPLEMENTARY 边；03_seed 预置 >=10 边覆盖演示技能簇。_避免_：只画雷达图/关系图而无类型化边、把 ECharts JSON 当本体、多 worker 各建一份图。

详见 ADR-0005、V4 Q5/Q11/Q21。

**可解释评分 (Explainable Scoring)**：
主分 = 维度化子分（技能按 `job_skill.importance` 加权命中、学历档差、经验比例、城市契合），权重可调，**不用黑箱向量打主分**。向量只做候选召回 + 同义增强，藏在 pipeline 里不对外呈现。`required_level`(MUST/NICE/BONUS) = 资格层级，`importance FLOAT(1~5)` = 同层级内细分权重；MUST->importance=5、NICE->3、BONUS->1 自动填入。CANDIDATE 技能按 `effective_hit = required_level_weight * confidence` 计入。skill 子分用 0~100 一致量表。INCLUDES 父子归一算法：JD 要父技能、用户会子技能，按 `0.6 * required_level_weight` 计入（父-子收）；JD 要子、用户会父，不计（子父不补）。图算法做增值项：技能簇 `community detection` -> 相近领域岗位；`PREREQUISITE` 反推 -> 学习前置链。双向推荐共用同一张 `match_result` 按方向读视图，不重算。`match_result` 改为按 (resume_id, job_id) 懒计算 + 新鲜度缓存：任一端请求推荐时后端先查 match_result，命中且 `updated_at` 晚于该简历/岗位技能最后变更时间则直接返回，否则调 AI 算、写回。召回前置在后端用 SQL + `skill_synonym` 同义扩展，候选集硬封顶 <=50，AI 仅传候选集。`match_detail(JSONB)` = `{score, breakdown{skill/edu/exp/city}, rationale(模板拼), graph_hints}`。_避免_：黑箱向量打主分、大模型直接打分、双向各算一次、`match_result.reason` 与 `rationale` 各存一份、全量岗位灌进 AI。

详见 ADR-0005、V4 Q1/Q2/Q15。

**推荐落点 (Recommendation Authority)**：
推荐评分、向量召回、图谱推理统一在 FastAPI 主服务内（core + infrastructure），是推荐 + 图谱的单一权威。后端把用户技能向量与候选岗位列表（<=50）传给内部推荐引擎，算分排序并产出 `match_detail`；`match_result` 与 `recommend_record` 的写库由 repositories 层统一负责。_避免_：另攀一套评分代码、跨进程调用。

详见 ADR-0005。

**职业规划 (Career Planning)**：
规划主力是 networkx 图算法：取目标 `occupation_role` 的 MUST 技能 - 用户已有 = 缺口集，沿缺口技能 `PREREQUISITE` 边拓扑排序得有序学习路径（结构化、可解释、可复现）。LLM 仅做自然语言润色：把 `{gap, path, target_role}` 喂 DeepSeek 输出通顺话，不改结构化结果，分数/路径不经大模型。**删「薪资预测」**（无数据源，违背「不用大模型编主分」原则）。`career_plan` 存结构化 JSON `{target_role, gap_skills[], learning_path[], graph_hints, rationale}` + 一列 LLM 润色句。目标 role 来源：职业规划页下拉选 occupation_role，或当前最高推荐岗位反推 occupation_role。_避免_：LLM 空谈规划、薪资预测、大模型编主分。

详见 V4 Q6。

**文件单一事实源 (File Single Source of Truth)**：
`upload_file` 是文件本体的唯一事实源；`resume` 通过 `file_id` 引用 `upload_file`，不再自存 `file_name/file_path/file_url/storage_type/file_type` 等字段；`parse_task` 同样引用 `file_id`。链路为 `upload_file -> resume -> parse_task`。清盘脚本 `starmap-cleanup.sh` 软删 7 天前 upload_file 与磁盘文件，留近 7 天演示样本。_避免_：`resume` 与 `upload_file` 双写文件字段导致漂移、`parse_task` 不指向 `file_id`。

详见 ADR-0008 D6、V4 Q12。

**岗位双模式 (Job Dual-Mode)**：
`job` 加 `source VARCHAR(MANUAL/UPLOAD)`。JD 手动填写直接填 `job` + `job_skill`（技能从字典下拉，必为 ACTIVE），不经 AI/parse_task；JD 文件上传则建 parse_task 走 AI。两种来源以 `source` 区分。_避免_：手填 JD 未经字典校验、手填与上传混淆无区分。

详见 V4 Q12。

**企业审核 (Company Audit)**：
`company` 加 `audit_status VARCHAR(UNVERIFIED/PENDING/VERIFIED/REJECTED)` + `audit_reason`。注册默认 UNVERIFIED，可发岗位但 `status=DRAFT` 不对外；管理员后台审核 -> PENDING -> VERIFIED 后岗位才 OPEN 对外；REJECTED 带 reason 企业端可见。未审企业岗位对外接口不返。演示预置企业账号 `audit_status=VERIFIED` 不影响流畅度。`user_profile` 加 `profile_completeness INT(0~100)` 作前端展示与推荐排序小权重。_避免_：企业随便填名注册即发岗位、未审岗位对外可见。

详见 V4 Q19。

**通知与商业闭环 (Notification & Business Loop)**：
`notification` 加 `is_read BOOLEAN`(默认 false) + `type VARCHAR`(APPLICATION/INTERVIEW_INVITE/SYSTEM)。求职者点推荐岗位投递 -> `recommend_record.is_clicked=true`，点「投递」-> `is_applied=true` + 给企业发 notification(type=APPLICATION)。企业端点推荐人才「发起面试邀请」-> 给求职者发 notification(type=INTERVIEW_INVITE) + `recommend_record` 加 `is_invited`。已读由用户点通知触发 `PUT /api/notification/{id}/read`；红点 = `is_read=false` 计数。前端轮询未读数 `GET /api/notification/unread-count` 每 30s。清理：保留近 30 天 + 自动软删超期行。_避免_：推荐之后无后续动作、通知无限增长无 TTL。

详见 V4 Q16/Q18、ADR-0010。

**分页约定 (Pagination)**：
统一分页参数 `page + size`，默认 `size=20`，`size <= 100`。所有 list 接口走分页，SQLAlchemy `offset/limit` + `select(func.count())` 计总数。分页返回 `{records, total, page, size}`。前端 Element Plus `el-pagination` 或 loadMore。推荐列表分页基于已缓存 `match_result`，「看更多」翻页不重调 AI。总量兜底：超 500 只返前 500 + 提示筛选。前端加载态统一：首屏 skeleton，接口 >1s 显示「加载中」，>5s 显示重试按钮。_避免_：无分页全量返回、推荐翻页重调 AI。

详见 ADR-0010、V4 Q17。

**鉴权 (Authentication)**：
统一用 python-jose + FastAPI Depends。`api/deps.py` 中 `get_current_user` 解析 JWT token，从 payload 提取大写角色（ADMIN/USER/COMPANY），通过 `oauth2_scheme` + `HTTPBearer` 注入。路由用 `Depends(require_role("ADMIN"))` 做角色校验。JWT claim 一律大写，与 ADR-0002 角色语义枚举口径一致。密码用 passlib bcrypt 加密。_避免_：自写白名单中间件、小写角色名、硬编码 token 校验。

详见 ADR-0006。

**国产化部署 (Domestic Deployment)**：
部署须跑在 LoongArch + 银河麒麟高级服务器版，数据库用国产 KingbaseES（赛题红线，不满足视为 0 分）。**裸部署优先**：KingbaseES 宿主安装、FastAPI 用 systemd 裸跑（`uvicorn app.main:app`）、Nginx 宿主跑静态；Docker 仅作可选非推荐路径。内存预算为「参考估值」待 day1-2 冒烟实测后回填。缓存用 aiocache 默认内存缓存兜底（JWT 黑名单 + 验证码 + 统计缓存），不做 DB 层数据缓存（KingbaseES 自身缓存够）。`install.sh` 无人值守从软件源装依赖、禁打包 site_packages/node_modules；依赖装不上即 `exit 1`。_避免_：Docker 全容器（8GB 紧张）、打包第三方依赖目录。

详见 ADR-0007、V4 Q9/Q20。

**界面形态 (UI Form Factor)**：
选 PC Web（B/S 架构），不做原生 App。赛题用「或」给了二选一，PC Web 在 LoongArch 麒麟虚机浏览器跑得起来即可满足。Vue3 一套代码同时撑 PC 演示与答辩。前端 Vue3 响应式布局兜底，手机浏览器能跑基本形态。_避免_：移动端原生框架（React Native / Flutter / uni-app）。

详见 ADR-0009。

**演示叙事 (Demo Narrative)**：
PPT 与视频同源，共用 `docs/演示叙事.md` 的 7 分钟 8 分镜，叙事弧：痛点开场 -> AI 结构化 -> 图谱缺口 -> 可解释匹配依据 -> 职业规划图路径 -> 企业端反向荐人 -> 麒麟虚机 `uname`/服务起来 -> 国产化收口。PPT = 分镜静态截图版，视频 = 分镜录屏版，口播稿共用。_避免_：按功能罗列平铺、PPT 与视频各做各。

详见 `docs/演示叙事.md`。