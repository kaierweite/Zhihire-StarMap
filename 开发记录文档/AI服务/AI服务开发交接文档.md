# AI 服务开发交接文档

> 本文件供新对话使用，复制以下内容作为开场白即可。

---

## 复制以下内容到新对话

```
我是智聘星图项目的开发者，现在要开始 FastAPI AI 微服务的代码开发。

## 项目背景
- 赛题：第十五届中国软件杯 B2 赛题，基于银河麒麟操作系统的 AI 智能匹配与能力图谱系统
- AI 服务技术栈：Python 3 + FastAPI + LangChain + networkx + 云端 DeepSeek API
- AI 服务是独立微服务，后端 Spring Boot 通过 HTTP 调用 AI 服务
- AI 服务不直写数据库，只负责计算和返回结果，由后端统一写库

## 当前状态
设计阶段已全部完成，AI 服务从 day01 开始。

## 关键约束（必须遵守）
1. FastAPI 框架，uvicorn 启动，--workers 1（单进程，内存图单份）
2. LLM 统一走云端 DeepSeek API（配置切换 endpoint/API Key）
3. 不用本地大模型（Ollama/Qwen 已废弃）
4. 不用 sentence-transformers（依赖 PyTorch，LoongArch 不兼容）
5. networkx 常驻内存图对象（lifespan 启动钩子从 DB 全量重建）
6. 文档解析用 pdfplumber + python-docx（docling 降级方案）
7. 服务端口：8000
8. 后端通过 HTTP 调用 AI 服务（不直写 DB）
9. 中文注释

## 目录结构
```
ai-service/
├── app/
│   ├── api/              # API 路由
│   │   ├── health.py     # /ai/health 健康检查
│   │   ├── parse.py      # /ai/parse/resume、/ai/parse/job
│   │   ├── recommend.py  # /ai/recommend/match
│   │   ├── graph.py      # /ai/graph/build、/ai/graph/reload
│   │   ├── career.py     # /ai/career/analyze
│   │   └── interview.py  # /ai/interview/*（出题/评答/报告）
│   ├── core/
│   │   ├── llm_client.py # DeepSeek API 调用封装
│   │   ├── parser/       # 文档解析（pdfplumber + python-docx）
│   │   ├── normalizer/   # 技能归一 prompt
│   │   ├── graph/        # networkx 图谱
│   │   └── recommender/  # 可解释维度子分
│   ├── models/           # Pydantic 数据模型
│   └── config.py         # 配置（DeepSeek endpoint/key）
├── main.py               # 启动入口（含 lifespan 钩子）
├── requirements.txt
└── config.py
```

## 后端调用 AI 服务的接口约定

| AI 接口 | 后端调用场景 | 入参 | 出参 |
|---------|------------|------|------|
| POST /ai/parse/resume | 简历解析 | file_path | raw_text, skills[], parsed_data |
| POST /ai/parse/job | 岗位 JD 解析 | file_path | skills[], occupation_role_name, requirements |
| POST /ai/recommend/match | 匹配评分 | user_skills[], candidates[] | match_results[{score, breakdown, rationale, graph_hints}] |
| POST /ai/graph/build | 构建图谱 | skills[], relations[] | graph_data(ECharts JSON) |
| POST /ai/graph/reload | 重建内存图 | — | status |
| POST /ai/career/analyze | 职业规划 | user_skills[], target_role | gap_skills[], learning_path[], rationale |
| POST /ai/interview/questions | 面试出题 | job_id, resume_id, count | questions[{type, content, expected_points}] |
| POST /ai/interview/evaluate | 面试题评分 | question_id, answer | score, feedback, matched_points[], missed_points[] |
| POST /ai/interview/report | 面试报告 | session_id | overall_score, radar{}, feedback[] |
| POST /ai/resume/optimize | 简历优化 | resume_id, job_id | suggestions[{section, current, suggestion}] |

## DeepSeek API 调用示例
```python
import httpx

async def call_deepseek(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=30.0
        )
        return response.json()["choices"][0]["message"]["content"]
```

## 工作流
Windows 本地开发 → git push → 麒麟虚机 git pull → uvicorn 启动

## 请从 day01 开始执行
读取「开发记录文档/AI服务/day01-项目初始化.md」，从第一个未勾选的任务开始。
```

---

## 使用说明

1. 打开新的 Codex 对话
2. 复制上面「复制以下内容到新对话」框内的全部文字
3. 粘贴发送
4. 新对话会从 FastAPI 项目初始化开始
