# 第8天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

搭建AI服务，部署Ollama + Qwen2.5:7B模型，设计简历解析Prompt模板，打通AI服务与后端的通信。

## 今日能力要求

- Python FastAPI（熟练）
- Ollama部署（基础）
- Prompt工程（熟练）

**最终产出：**

```text
ai-service/
├──app/
│   ├──main.py                # FastAPI入口（含API路由）
│   ├──config.py              # 配置文件
│   ├──services/
│   │   ├──llm_service.py     # LLM调用封装
│   │   └──prompt_templates.py # Prompt模板
│   ├──models/
│   │   └──schemas.py         # 请求/响应模型
│   └──utils/
│       └──helpers.py         # 辅助函数
├──ollama/
│   └──README.md              # Ollama部署说明
├──requirements.txt
└──test/
    ├──test_prompt.py         # Prompt测试
    └──test_llm.py            # LLM调用测试
```

---

# 第一阶段：部署Ollama（1小时）

## 任务1：安装Ollama

```bash
# Windows
# 下载 https://ollama.com/download/OllamaSetup.exe 安装

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Docker方式
docker run -d --name ollama -p 11434:11434 ollama/ollama
```

## 任务2：拉取模型

```bash
# 拉取Qwen2.5（7B参数版本）
ollama pull qwen2.5:7b

# 验证模型是否正常运行
ollama run qwen2.5:7b "你好，请介绍一下你自己"

# 检查API是否可访问
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "你好",
  "stream": false
}'
```

## 任务3：Ollama配置建议

```bash
# 设置模型最大上下文（Ollama默认2048，建议设4096）
# Windows: 环境变量 OLLAMA_CONTEXT_LENGTH=4096
# Linux: export OLLAMA_CONTEXT_LENGTH=4096

# 设置并发请求数（默认1，如果GPU显存够可适当提高）
# export OLLAMA_NUM_PARALLEL=1

# 设置模型保持加载（避免频繁加载/卸载）
# export OLLAMA_KEEP_ALIVE=5m
```

---

# 第二阶段：AI服务配置文件（30分钟）

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Ollama配置
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:7b"
    llm_temperature: float = 0.1  # 简历解析用较低温度，保证准确性
    llm_max_tokens: int = 2048
    llm_context_length: int = 4096

    # 服务配置
    service_port: int = 8000
    service_host: str = "0.0.0.0"

    # Redis配置（用于缓存）
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # 后端服务地址
    backend_url: str = "http://localhost:8080"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

# 第三阶段：Prompt工程设计（1.5小时）

## 任务1：简历解析Prompt

```python
# prompt_templates.py

RESUME_PARSE_PROMPT = """
你是一个专业的简历解析AI助手。请从以下简历文本中提取结构化信息。

## 简历文本
---
{resume_text}
---

## 要求
1. 仔细阅读简历文本，提取所有能找到的信息
2. 如果某字段在简历中未提及，请设置为 null
3. 技能标签请规范化，如"Java"不要写成"java"，保持首字母大写
4. 工作年限精确到年，如 "3.5"
5. 学历取最高学历

## 输出格式（必须是JSON）
```json
{{
    "personal_info": {{
        "name": "姓名",
        "phone": "手机号",
        "email": "邮箱",
        "city": "所在城市"
    }},
    "education": {{
        "school": "毕业学校",
        "degree": "最高学历（博士/硕士/本科/大专）",
        "major": "专业",
        "graduation_year": "毕业年份"
    }},
    "work_experience": [
        {{
            "company": "公司名称",
            "position": "职位",
            "start_date": "开始时间",
            "end_date": "结束时间",
            "description": "工作描述",
            "tech_stack": ["技术栈1", "技术栈2"]
        }}
    ],
    "project_experience": [
        {{
            "name": "项目名称",
            "role": "担任角色",
            "description": "项目描述",
            "tech_stack": ["技术栈1", "技术栈2"]
        }}
    ],
    "skills": ["技能1", "技能2", "技能3"],
    "certifications": ["证书1"],
    "self_evaluation": "自我评价",
    "summary": {{
        "total_experience_years": 3.5,
        "highest_education": "本科",
        "skill_count": 8,
        "project_count": 3
    }}
}}
```

请直接输出JSON，不要包含其他内容。
"""
```

## 任务2：岗位JD解析Prompt

```python
JOB_PARSE_PROMPT = """
你是一个专业的岗位需求分析AI助手。请从以下岗位描述中提取结构化信息。

## 岗位描述
---
{job_text}
---

## 输出格式
```json
{{
    "position_info": {{
        "title": "岗位名称",
        "department": "所属部门",
        "location": "工作地点（城市）"
    }},
    "requirements": {{
        "education": "学历要求",
        "experience_min": "最低工作年限（年）",
        "skills_must": ["必备技能1", "必备技能2"],
        "skills_plus": ["加分技能1", "加分技能2"],
        "other_requirements": ["其他要求1"]
    }},
    "responsibilities": ["岗位职责1", "岗位职责2"],
    "salary_range": {{
        "min": "最低薪资（万元/年）",
        "max": "最高薪资（万元/年）"
    }},
    "benefits": ["福利1", "福利2"],
    "summary": {{
        "key_skills_count": 5,
        "experience_level": "初中级/高级/专家",
        "work_type": "全职/兼职/实习"
    }}
}}
```
"""
```

## 任务3：Prompt优化原则

```text
简历解析Prompt设计原则：

1. 角色设定
   - 明确告诉AI它是"专业简历解析助手"
   - 设定专业身份可以提高输出质量

2. 输出结构
   - 用JSON Schema约束输出格式
   - 给示例值让AI理解字段含义
   - 枚举值用括号给出选项

3. 容错处理
   - 要求缺失字段返回null而非跳过
   - 设置temperature=0.1避免创造性输出
   - 输出长度限制2048 tokens

4. 技能规范化
   - 要求首字母大写
   - 常见同义词统一：js→JavaScript, vue→Vue.js
```

---

# 第四阶段：LLM调用封装（1小时）

## 任务1：LLM服务

```python
# llm_service.py
import json
import httpx
from typing import Optional
from config import settings

class LLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """调用Ollama生成文本"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "stream": False
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

    async def parse_json_response(self, text: str) -> dict:
        """从LLM响应中提取JSON"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试从```json 块中提取
        import re
        match = re.search(r"```(?:json)?\n(.+?)\n```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试从{开始到}结束
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError("无法解析LLM输出为JSON")

llm_service = LLMService()
```

## 任务2：健康检查和模型管理

```python
@app.get("/health")
async def health_check():
    """AI服务健康检查"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            models = response.json().get("models", [])
            return {
                "status": "ok",
                "service": "ai-service",
                "llm_model": settings.llm_model,
                "ollama_models": [m["name"] for m in models]
            }
    except Exception as e:
        return {
            "status": "error",
            "service": "ai-service",
            "error": str(e)
        }
```

---

# 第8天验收标准

必须完成：

✅ Ollama已安装并运行

✅ Qwen2.5:7B模型已下载

✅ Ollama API可正常调用

✅ AI服务可启动（uvicorn）

✅ 简历解析Prompt设计完成

✅ 岗位解析Prompt设计完成

✅ LLM调用封装完成

✅ JSON结果提取成功

✅ Prompt测试通过（至少测试3份不同格式简历）

✅ Git已提交

---

# 常见问题

**Q：Ollama启动报错？**

A：检查是否已安装Ollama，Windows需要以管理员身份运行。

**Q：模型下载慢？**

A：Qwen2.5:7B约4.5GB，建议使用阿里云国内镜像或提前下载。

**Q：Ollama API超时？**

A：首次调用需要加载模型到内存，约需10-30秒。后续调用会快很多。

**Q：AI输出JSON格式不对？**

A：在Prompt中加强格式约束，并在代码中加入JSON修复逻辑。
