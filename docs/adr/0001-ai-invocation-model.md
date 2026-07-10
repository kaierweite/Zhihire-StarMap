# AI 算力全走云端大模型 API

简历解析、岗位解析、职业规划、推荐打分**全部走云端 DeepSeek API**。系统的 AI 算力统一交由云端大模型承担，不在演示机上本地加载或运行任何大模型。

模型「可切换」不做成用户可见的本地/云端开关,而是体现为**配置项指向不同的云端 endpoint / API Key**(DeepSeek 为主,可挂备用云厂商)。把它当成运维级配置,不当作答辩演示点。

## 决策驱动

V2 grilling(Q1)否决了「HR 在企业设置页切换 DeepSeek / 本地 Ollama-Qwen2.5」的旧设计,理由如下:

- **赛题红线**:"软件需部署在自主指令系统 LoongArch 架构 + 麒麟高级服务器版运行,不满足视为 0 分。"演示机为四核 CPU、8GB 内存、256GB 硬盘。
- **LoongArch 不可靠**:loongarch64 上没有稳定的 PyTorch wheels;本地 7B 模型推理(llama.cpp loongarch64 构建 + 量化)路径未经验证,内存占用实测验算 KingbaseES + Redis + FastAPI 已占去大部分,7B 模型会让 8GB 主机吃紧甚至演示假死。
- **风险收益不划算**:本地模型换来"可看见切换"的两秒演示动效,赔上的是 0 分级别的部署可行性与演示稳定性。

### 演示机硬约束(写入本 ADR 作为后续所有容量规划的前提)

| 维度 | 约束 |
|------|------|
| CPU | 自主指令集 LoongArch 架构,四核 |
| 内存 | 8GB 以上 |
| 磁盘 | 256GB 以上 |
| 操作系统 | 银河麒麟高级服务器版 V11/V10 |
| 数据库 | 国产数据库(KingbaseES) |

凡是会让上述任一项超载的技术选择(本地大模型、PyTorch/torch、重型 GPU 推理),一律不引入。

## Considered Options

- **A 全局 DeepSeek API(采纳)**:实现最简,云端算力不压演示机,演示稳定性最高;离线风险用「DeepSeek 为主、备用云厂商为备」的配置级切换对冲。
- **B 全局本地模型**:已在 Q1 否决——LoongArch 兼容性未验证、8GB 内存拉满、演示假死风险。
- **C 双模式带 HR 可见开关(旧设计,已否决)**:本地链路被演示的收益不抵 0 分级风险,且 Q1 已确认不赌本地模型演示点。

## Consequences

- AI 服务抽象一个统一 `LLMClient`,按配置项选择云端 endpoint/Key(DeepSeek / 备用云);废弃本地 Ollama/Qwen2.5 实现分支。
- 简历解析、岗位解析、职业规划、推荐打分四条链路 prompt 模板与输出 JSON 结构统一,不区分本地/云端。
- **embedding 不走本地 sentence-transformers**:依赖 PyTorch,被本 ADR 硬约束排除;embedding 用云端接口,退路为 BM25/TF-IDF(见 ADR-0005)。
- 部署文档中删除「本地大模型回退」相关缓解措施。
- 答辩演示点改为「可解释匹配依据 + 知识图谱推理 + 麒麟虚机端到端跑通」(见 `docs/演示叙事.md`),不再以本地模型为卖点。

## 关联

- 本 ADR 的容量约束被 `ADR-0007` 国产化部署约束继承并细化。
- 技术栈描述同步删除 `sentence-transformers`(见 V2 决策记录 Q1)。
