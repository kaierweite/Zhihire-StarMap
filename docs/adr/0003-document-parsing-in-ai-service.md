# 文档解析统一收敛于 AI 服务 + 技能归一产出契约

## 一、文本抽取与结构化落点

简历与岗位文档的文本抽取和结构化解析一律在 Python AI 服务完成(docling + pdfplumber + python-docx),后端只负责接收文件、落库保存、调用 `/ai/parse/*` 并把返回的 `raw_text` 与结构化 JSON 持久化。day01 提到的 PDFBox/Apache POI/Tika(Java 端解析)不再采用。

解析质量直接喂给演示里最显眼的能力图谱与推荐,Python 这套对扫描件、乱版 PDF 更稳;把解析收在 AI 服务一侧,也让后端不必为 docling 在 LoongArch/麒麟上攒一套未必好装的 Java 桥。代价是 AI 服务要管文件流(接收后端转发的文件或路径),但换来的是单一解析实现,避免后端与 AI 双端各写一遍。

> LoongArch 可得性兜底:docling 若在某版本缺 loongarch64 wheel,**降级纯 Python** 以 pdfplumber + python-docx 统揽(赛题只要求 PDF/DOC 解析,docling 是锦上添花,非必要)。见 `ADR-0007`。

## 二、技能归一产出契约(V2 grilling Q3 新增)

解析的下游全是结构化关联表(`user_skill`、`job_skill`、`skill_relation`、`role_skill`),全部按 `skill.id` 连。因此从 `parsed_data` 到 `user_skill`/`job_skill` 之间,必须有一道「技能标准化 / 字典归一」工序。本 ADR 把这道工序的产出契约钉死。

### AI 侧职责

AI 解析时在 prompt 里给一份精简版技能字典(一级名 + 高频二级名,控制 token),让大模型把简历/JD 技能映射到字典既有 `skill_id`;映射不上的,AI **不生成新 skill_id**,而是输出如下结构:

```json
{
  "raw": "SpringBoot",
  "canonical_name": "Spring Boot",
  "confidence": 0.9
}
```

- 每个技能元素都带 `raw`(原文本)、`canonical_name`(归一后的标准名)、`confidence`(置信度 0~1)。
- `raw` 保留给前端解析结果展示;`canonical_name` 给后端查字典。
- AI 只负责产出归一名,**不决定是否新建字典行**。

### 后端侧职责

后端收到 AI 的 `canonical_name`:

1. 按 `canonical_name` 唯一索引查 `skill` 表。查到则复用该 `skill_id`。
2. 查不到则触发入库新技能流程,落地为 `skill.status = CANDIDATE`,不立即进图谱关系和推荐;记 `raw_text` 来源供后台审核。

### 字典三级状态(详见 `ADR-0002` 语义枚举口径)

- `ACTIVE`:正式技能,参与图谱边(`skill_relation`/`role_skill`)与匹配主分。
- `CANDIDATE`:AI 归一未命中的新词,参与匹配但带 `confidence` 折扣,**不进图谱边**;待人工校准后转 `ACTIVE`,自动纳入图谱与推荐。
- `MERGED`:与另一技能合并(通过 `merge_target_id` 指向新 `skill`),原行不再被引用。

### 兜底入口

后台新增「技能字典审核页」(见 `prototype/admin/技能字典审核.drawio`),作为 AI 归一不准时的人工修正入口——这是 `CONTEXT.md` 风险表「AI 解析准确率不足 → 支持人工修正」的落点。

## Considered Options

- **A 后端做归一(AI 只出文本)**:后端拿原始技能文本查字典。简单但 AI 已有上下文与语义判断能力,浪费且易因同形异义误并。
- **B AI 直出 skill_id 并可造新**:大模型在 prompt 里被要求输出 skill_id 并允许新建——`hallucination` 风险高,字典会野蛮生长,图谱边建不稳。
- **C AI 出归一名 + 后端查表兜底(采纳)**:分工最稳,AI 不造 id、字典可控扩张,冷门技能不漏匹配也不乱并。

## Consequences

- AI 服务解析 prompt 输出规范强制上述 `{raw, canonical_name, confidence}` 结构。
- 后端需实现按 `canonical_name` 查表 + `CANDIDATE` 入库分支。
- `skill` 表加 `status`(`ACTIVE/CANDIDATE/MERGED`)、`merge_target_id` 字段;新增 `skill_synonym` 同义表(详见 V2 决策记录 Q3 与 day02 表结构变更)。
- `CANDIDATE` 技能参与匹配但带 confidence 折扣;`ACTIVE` 才上图谱边。
- 后台加技能字典审核页(候选词审核、同义合并、状态流转)。
