# Day07 职业规划模块 — 对话交接文档

> 本对话已完成 Day06 匹配推荐模块，即将开启 Day07。
> 以下信息是从当前代码库现状提取的交接内容，供下一对话直接使用。

---

## 项目状态

### 已完成的模块
认证 / 用户档案 / 简历 / 技能字典 / 企业 / 岗位(9端点) / 匹配推荐(4端点) / 能力图谱(4端点) / 投递

### Day07 要做的
基于用户能力图谱缺口分析，为目标职业角色生成有序学习路径。

---

## 现有可用的相关代码

### 数据库表（01_schema.sql 已定义，但无 migration）
- career_plan 表：id BIGSERIAL, user_id BIGINT, target_role VARCHAR(100), plan_content JSONB, source VARCHAR(20), created_at, updated_at, deleted_at

### 核心算法（已有基础但不够）
- backend/app/core/career/career_engine.py：已有三个函数
  - analyze_skill_gap() — 缺口分析（MUST→NICE→BONUS 排序）
  - recommend_career_paths() — 基于匹配度推荐职业路径
  - build_learning_path() — 沿 PREREQUISITE 边拓扑排序
  - 文档要求拆为 planner.py + gap_analyzer.py

### 完全空缺（需新建）
- api/v1/career.py — 不存在
- services/career_service.py — 不存在
- repositories/career_repository.py — 不存在
- models/entities/career_plan.py — 不存在
- models/schemas/career.py — 不存在

### 图谱基础设施（Day04 已有，可直接用）
- core/graph/builder.py — skill_graph 全局单例 networkx.DiGraph
- core/graph/__init__.py 导出 skill_graph, build_graph, reload_graph
- SkillGraphHolder 类管理图生命周期

### 角色数据（Day04 已有）
- role 表 + Role 实体 — 职业角色
- role_skill 表 + RoleSkill 实体 — 角色技能要求
- role_repository 有 list_active(), get_by_id(), get_by_name()
- role_skill_repository 有 list_by_role() 返回 list[tuple[RoleSkill, Skill]]
- skill_relation_repository 有 list_by_skill() 和 list_active()

### LLM 客户端（用于末句润色）
- infrastructure/llm/deepseek_client.py — DeepSeekClient 类
- chat() 支持 system prompt + user message
- 无 API key 时返回 mock 数据

### 已有重叠代码（注意不要重复）
- services/graph_service.py 的 analyze_gap_with_role() 已做了缺口分析
- Day07 的 career_service 不应复用 graph_service，但可以参考实现模式

### 迁移链
- 最新 revision：b0c1d2e3f4a5（Day06b）
- 需新建 migration 创建 career_plan 表
- down_revision = "b0c1d2e3f4a5"

### 软删除规范
- 所有表 deleted_at VARCHAR(1) DEFAULT "0"，查询过滤 deleted_at == "0"

---

## Day07 文档要求（来自开发记录文档/后端/day07-career职业规划模块.md）

### 两个 API 端点
1. POST /api/career/plan/generate — USER 角色
   - 参数：target_role_id (int)
   - 运行算法 → 写入/更新 career_plan → 返回结果

2. GET /api/career/plan — USER 角色
   - 获取当前用户已生成的职业规划

### 算法流程
1. 用户选目标 role
2. 取 role_skill MUST 技能集 − user_skill 已有 = gap_skills
3. 对 gap_skills 沿 PREREQUISITE 边做拓扑排序 → learning_path
4. 附加 graph_hints：SIMILAR 关联、COMPLEMENTARY 补充
5. rationale 末句由 LLM 润色（不改变结果）
6. source 区分来源：INTERVIEW / PROACTIVE / RECOMMEND

### 响应结构
{
  "target_role": "前端工程师",
  "gap_skills": [{"skill_name": "Kafka", "requirement_level": "MUST"}],
  "learning_path": [["HTML", "CSS", "JavaScript", "Vue 3"]],
  "graph_hints": ["您已掌握React（与Vue 3相似），可快速上手"],
  "rationale": "您与目标岗位的技能匹配度为65%，主要缺口为Kafka等3项必备技能..."
}

### 代码分层
| 层 | 文件 | 说明 |
| 路由 | api/v1/career.py | 新建 |
| 服务 | services/career_service.py | 新建 |
| 核心 | core/career/planner.py | 新建，networkx 拓扑排序 |
| 核心 | core/career/gap_analyzer.py | 新建，缺口分析 |
| 仓储 | repositories/career_repository.py | 新建 |
| 实体 | models/entities/career_plan.py | 新建 |
| 模型 | models/schemas/career.py | 新建 |

### 验收标准
- [ ] 选择角色 → 返回缺口技能 + 有序学习路径
- [ ] 学习路径按 PREREQUISITE 拓扑排序
- [ ] 分数/路径不经大模型
- [ ] rationale 是模板拼接 + LLM 末句润色

---

## 已知陷阱

1. Role 实体的 id 是 graph_service 的 role_id（role 表），不是 occupation_role 表的 id
2. build_learning_path() 用 G.predecessors(node) 取前驱，但 skill_relation 表的 PREREQUISITE 边方向是 skill_id_a → skill_id_b（a 是 b 的前置）
3. career_engine.py 的 build_learning_path 目前用 nx.Graph（无向图），拓扑排序需要 nx.DiGraph（有向图）
4. 所有 JSONB 字段用 json.dumps(data, ensure_ascii=False) 序列化
5. Numeric 类型字段返回 Decimal，序列化前需要 float() 转换
6. 实体必须注册到 models/entities/__init__.py 的 __all__ 中
7. 路由必须注册到 api/v1/__init__.py
8. 迁移是手写，不用 --autogenerate
9. 新创建的模块（如 career_repository）被 import 时，repositories/__init__.py 为空也可以，因为 from app.repositories import career_repository 会按文件名自动发现
