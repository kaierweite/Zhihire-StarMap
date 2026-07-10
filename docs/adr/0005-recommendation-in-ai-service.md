# 推荐评分、能力图谱、知识图谱推理归口于 AI 服务

## 一、单一权威

推荐评分、向量召回、能力图谱与知识图谱推理统一在 AI 服务(Python)一侧。AI 服务是推荐与图谱的单一权威:图谱权威在 AI 服务**内存中的 networkx 图对象**;`ability_graph` 表只缓存渲染用 ECharts payload,DB 不是图谱本身。

后端把用户技能向量与候选岗位列表传 `/ai/recommend/match`,AI 算分排序并产出 `match_detail` 后回结果;`match_result` 与 `recommend_record` 的写库由后端统一负责,AI 服务不直写 DB。

把推荐和图谱收在同一处,避免后端再攀一套评分代码与向量预处理,也让演示中「推荐 + 图谱」两张图由同一权威产出、口径一致。

## 二、可解释评分算法(V2 grilling Q4)

**取消** day14 拍脑袋的固定权重「技能 50% + 经验 20% + 学历 20% + 城市 10%」,改为维度化子分再合成,权重可调,主分**不**用黑箱向量。

### 主分 = 可解释维度子分

| 维度 | 计算 |
|------|------|
| 技能 | 命中必备技能按 `job_skill.importance` 加权;加分技能软匹配;`CANDIDATE` 技能按 `confidence` 折扣计入 |
| 学历 | 量化档差:JD 要本科、简历硕士即满分,低一档打折扣 |
| 经验 | 工作年限达标比例 |
| 城市 | `user_profile.current_city` / `target_city` 与岗位 `city` 契合加分 |

每个子分自带一根「依据」:命中哪些必备技能、缺了哪几个加分项、学历差几档、城市契不契。总分按可调权重合成。**这正是赛题要的「匹配度评分与依据」。**

### 向量:只做召回,不打主分

embedding 用云端接口(ADB 设硬约束排除 sentence-transformers),退路为 BM25/TF-IDF。向量用于:

- 候选岗位 / 候选人粗召回;
- 技能归一同义增强(接 `skill_synonym`)。

向量作为基础设施藏在 pipeline 里,**不作为对外得分**。

### 图算法:增值项,非主分

`networkx` 图(常驻 AI 服务内存)用在两个「加分点」:

1. 技能簇 `community detection` → 「推荐你相近技能领域岗位」。
2. `PREREQUISITE` 边反推 → 「为补齐缺失技能 X,建议先学其前置 Y」,产出有序学习链(拓扑排序 / 最短路径)。

图算法产出物变成 `match_detail.graph_hints` 与职业规划的缺口学习路线,**不直接打分**。

### 双向推荐共用一次计算

(用户视角看到岗位、企业视角看到人才)看向同一张 `match_result` 按方向读出不同视图,不二次重算。`recommend_record.recommend_type` 区分 `JOB` 与 `TALENT` 两类推送。

## 三、技能图谱轻量本体(V2 grilling Q2)

图谱不是「ECharts 关系图 + 关联表」,而是有类型化边的知识图谱:

- `skill_relation` 表:`skill_id_a`、`skill_id_b`、`relation_type`(`PREREQUISITE / INCLUDES / SIMILAR / COMPLEMENTARY`)、`weight`。`skill` 自引用层级收进 `INCLUDES` 边。
- `role` 表(职业角色)+ `role_skill` 关联表(`requirement_level`:`MUST / NICE / BONUS`)。「职业路径推荐」有图依据:角色 → 角色有晋升边,技能 → 角色有必备边。
- `ability_graph` 表只存渲染用 ECharts JSON;图谱本体与算法在 AI 服务内存图对象上跑(技能字典规模小,几千节点内存常驻足够)。

## 四、match_detail 产出契约

`match_result.match_detail(JSONB)` 固定结构:

```json
{
  "score": 87,
  "breakdown": {
    "skill": { "score": 8.7, "hit": ["Java","Spring Boot","Redis"], "miss": ["Kafka"], "detail": "命中 8/10 必备,缺 1 加分" },
    "edu": { "score": 10, "detail": "硕士,达标+1档" },
    "exp": { "score": 9, "detail": "5 年,达标" },
    "city": { "score": 10, "detail": "居住/意向城市与岗位一致" }
  },
  "rationale": "命中 8/10 必备技能、学历超标、补 1 个加分技能即可达 90+",
  "graph_hints": ["为补齐 Kafka,建议先复习其消息可靠性前置知识"]
}
```

`rationale` 由后端按 `breakdown` **模板拼接**(成本低、可控、可双语),不让大模型去逐条生成分数解释。图路径那段可选地让大模型润色成一句自然话(输入是已算出的结构化结论,输出是润色),分数不经大模型。

## Considered Options

- **A 黑箱向量打主分**:最热但评审一句「这 87 分怎么来的」没结构化依据,丢创新分。
- **B 大模型直接打分**:最不可控,且贵。
- **C 可解释子分主分 + 向量召回 + 图增值 + 双向共用 + 模板拼 rationale(采纳)**:与 Q2/Q3 的可解释地基对齐,演示能逐条点开「依据」。

## Consequences

- 后端实现 `breakdown` 子分计算 + 模板拼接 `rationale`,并落实 `user_skill`/`job_skill` 关联填充(依赖 ADR-0003 的归一产出)。
- AI 服务:常驻 `networkx` 图对象、召回 embedding(云端或 BM25)、`PREREQUISITE` 反推学习链、技能簇 community detection。
- `user_profile` 补 `current_city`(赛题居住城市加分,当前字段缺)。
- `ADR-0001` 已排除 sentence-transformers,本 ADR 的 embedding 链路以云端接口/BM25 兜底。
