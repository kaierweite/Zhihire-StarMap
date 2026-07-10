# ADR-0011 面试能力培养模块（模拟面试 + 面试报告 + 面试题库 + 简历优化）

> 状态：Accepted（2026-07-04）
> 继承：V4 22 条决策 + ADR-0001~0010。本 ADR 仅补增量，不冲突既有口径。
> 触发：在原「匹配 + 图谱 + 规划」招聘闭环之外，新增「模拟面试训练」用户故事，
> 形成求职者端第二核心闭环。本 ADR 只覆盖文本链路，语音/视频多模态明确标为愿景。

---

## 背景

原系统核心闭环为「简历解析 → 能力图谱 → 人岗匹配 → 职业规划 → 企业反向荐人 + 面试邀请」，
「面试」只出现在企业端发起面试邀请通知这一动作里，不构成训练。

新增用户故事：求职者从数据库读取用户信息 + 岗位信息 → 启动模拟面试 →
AI 对应答进行分析与建议 → 基于回答质量 + 简历岗位匹配度生成面试报告
（能力雷达图 + 维度评分 + 反馈建议）→ 据反馈建议触发特定知识图谱缺口 + 学习路径 →
针对特定企业岗位生成面试题训练 → 简历优化建议。

该闭环与既有招聘闭环共享基建（简历解析、岗位/JD、能力图谱、职业规划学习路径、
match_detail 评分），不另起炉灶，仅在既有骨架上增链路。

---

## 决策

### D1 范围钉死：只做文本链路，多模态标愿景

- 本期只做 **文本式模拟面试**：LLM 扮演面试官，基于岗位 JD + 用户简历技能生成问题、
 评判回答、产出面试报告。
- 语音情感语调分析、视频微表情分析 **明确标为愿景，不上演示**：
  - 语音需引入国产语音云 API（讯飞/百度/阿里），打破 ADR-0001「DeepSeek 为主可切换
    备用」的单一文本链路，增一条云端依赖与不稳定面。
  - 视频微表情在 LoongArch 4 核 8GB 上算力不足、wheel 缺失（ADR-0007/V4 Q9 内存预算
    峰值预留 ~2GB），且无现成「微表情云端 API」，强行上必被评委追问「模型在哪跑」翻车。
  - 二者遵循 V4 既有原则：无数据源/算力不够的功能不做，避免演示被追问。

### D2 模拟面试为「第二核心闭环」，与招聘闭环并行

- 不改造原招聘闭环，模拟面试作为求职者端独立一级入口，与「岗位推荐」「能力图谱」
  「职业规划」并列。
- 共享 `user` / `resume` / `job` / `skill` / `skill_relation` / `occupation_role`
  / `match_result` 既有表，不重复存。
- 模拟面试可由两个入口触发：
  - 从「岗位详情」或「岗位推荐」点「针对该岗位模拟面试」（job_id 绑定）。
  - 从「模拟面试」一级页直接开始（按用户最高 occupation_role 推荐岗位或自选）。

### D3 新增 5 张表，22 → 27 表

| # | 表 | 说明 | 三时间字段 |
|---|----|------|-----------|
| 23 | `interview_session` | 面试会话（user_id、job_id 可空、occupation_role_id、status） | 全 |
| 24 | `interview_question` | 面试问题（session_id、question_type、content、expected_points JSONB） | 全 |
| 25 | `interview_answer` | 用户回答（question_id、content、ai_score、ai_feedback） | 全 |
| 26 | `interview_report` | 面试报告（session_id、overall_score、radar JSONB、feedback JSONB） | 全 |
| 27 | `resume_optimization` | 简历优化建议（resume_id、job_id 可空、suggestions JSONB） | 全 |

- 所有表沿用 ADR-0002：状态字段 VARCHAR 大写语义枚举。
- `interview_session.status`：`PENDING/IN_PROGRESS/COMPLETED/ABORTED`。
- `interview_question.question_type`：`TECHNICAL/BEHAVIORAL/SITUATIONAL/RESUME_BASED`。
- `interview_report.radar JSONB`：`{communication, technical, problem_solving, culture_fit, depth}`，
  各 0~100，直接喂 ECharts radar。
- `resume_optimization.suggestions JSONB`：`[{section, current, suggestion, relates_to_skill}]`。

### D4 AI 编排：四条链路汇总方案收口在 AI 服务

四条链路全走红端 DeepSeek，沿用 ADR-0001「配置项指向不同云厂商 endpoint」模型，
不引本地模型：

1. **简历解析**（已有，ADR-0003）。
2. **匹配评分**（已有，ADR-0005 可解释维度子分）。
3. **模拟面试问答**（新增）：
   - 出题：`POST /ai/interview/questions` 入参 `{session_id, job_id, resume_id, count}`，
     AI 据 JD + 用户技能输出 `{questions:[{type, content, expected_points}]}`，
     后端写 `interview_question`。
   - 评答：`POST /ai/interview/evaluate` 入参 `{question_id, answer}`，
     AI 输出 `{score 0~100, feedback, matched_points[], missed_points[]}`，
     后端写 `interview_answer`。
   - 报告：`POST /ai/interview/report` 入参 `{session_id}`，
     AI 汇总所有回答 + 复用 `match_detail` breakdown 产出 `{overall_score, radar, feedback}`，
     后端写 `interview_report`。
4. **简历优化**（新增）：
   - `POST /ai/resume/optimize` 入参 `{resume_id, job_id 可空}`，
     AI 据 `match_detail` 缺口 + 简历 raw_text 输出 `{suggestions[]}`，
     后端写 `resume_optimization`。

- 面试报告的 radar 维度与 `match_detail` 的 breakdown 对齐：technical 吸收 skill 子分，
  communication/problem_solving 由回答 AI 评产出，culture_fit 由 JD 关键词 + 回答匹配，
  depth 由 `PREREQUISITE` 链深度推断（复用既有可能图算法）。

### D5 面试报告复用图谱与学习路径管线

- 面试报告的「反馈建议」产出 gap 技能集后，**直接喂入既有职业规划管线**（V4 Q6，
  networkx PREREQUISITE 拓扑排序得有序学习路径），不另写一套。
- 触发方式：面试报告生成后，`POST /ai/career/plan` 入参带 `source=INTERVIEW` + gap 集，
  `career_plan` 复用存结构化 JSON + LLM 润色句列契约不变，仅 `rationale` 末句加「
  基于本次模拟面试反馈」来源。
- 不新增 career_plan 字段，`source VARCHAR(INTERVIEW/PROACTIVE/RECOMMEND)` 仅作可选元数据，
  不强制。

### D6 面试题库：按企业岗位生成，不爬外部数据

- 面试题不爬取外部题库，纯由 AI 据 `job` JD + `occupation_role_skill` 生成。
- 已生成的 `interview_question` 在题库页可复用：题库列出按 job/role 维度的题目，
 供面试前刷题。
- 题库不单独建表：复用 `interview_question`，加 `is_bank_visible BOOLEAN`（默认 false，
 报告生成后题库可见）。改 `interview_question` 加该字段。
- 不做「错题本」闭环，时间不够，标为后续扩展。

### D7 原型新增 4 页，求职者端一级菜单 7 → 8 项

- `prototype/user/模拟面试.html` — 入口：选岗位/职业角色 + 开始 + 进行中问答界面。
- `prototype/user/面试报告.html` — 报告：能力雷达图 + 维度评分 + 反馈建议 + 学习路径入口。
- `prototype/user/面试题库.html` — 按 job/role 维度的题目列表 + 题目卡片。
- `prototype/user/简历优化.html` — 优化建议列表（按 section）。
- 「模拟面试」「面试报告」「面试题库」「简历优化」中，「面试报告」为模拟面试的二级页（
  报告从模拟面试点进），不进一级菜单，故一级菜单净增 3 项：7 → 10 项。
  调整：求职者端一级菜单 7 → 10 项（模拟面试、面试题库、简历优化为新增一级页）。

### D8 演示叙事加 2 分镜

原 8 分镜 + 2 = 10 分镜（演示总时长仍按 7 分钟内控）：
- 镜 X「模拟面试」：选岗位 → AI 出题 → 回答 → AI 即时评分反馈。
- 镜 Y「面试报告 + 学习路径 + 简历优化」：能力雷达图 + 反馈 → 一键生成学习路径
  → 看简历优化建议。
- 视频内不演示语音/视频多模态。叙事稿口播提「未来支持语音情感/视频微表情分析」一句，
  作为愿景收尾，避免被追问。

---

## 影响文档

- 本 ADR（新建）。
- `database/README.md`：22 → 27 表，新增 5 表 + `interview_question.is_bank_visible`。
- `CONTEXT.md`：刷新项目简介、核心功能、当前状态、已知风险表。
- `README.md`：求职者端核心功能 + 模拟面试闭环；原型页数 23 → 27。
- `docs/V4决策记录.md`：补 Q23 面试模块增量条款。
- `docs/演示叙事.md`：加 2 分镜。
- `prototype/README.md` + 4 个新 HTML。
- `docs/项目目录结构.md`：backend module 增 `interview` 域（`module.interview.*`）。

---

## 已知风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| 面试问答 LLM 编排出题质量不稳 | 中 | 出题 prompt 钉死结构化 JSON 契约 + expected_points 供评答对齐 |
| 33h 窗口内前端三端全量不现实 | 高 | 本 ADR 钉设计层全量；代码层按 33h 分段执行方案优先核心闭环 |
| 语音/视频多模态缺位影响演示得分 | 低 | 口播一句愿景，不演示；避免无源功能被追问翻车 |
| interview_report radar 与 match_detail breakdown 口径漂移 | 中 | D4 明确 mapping，technical 吸 skill 子分，不重算 |
