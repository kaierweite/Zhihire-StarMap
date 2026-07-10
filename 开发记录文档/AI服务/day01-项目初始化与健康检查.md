# Day 01 — 项目初始化 + 健康检查

> **前置依赖**：Python 3.11+ 已安装

---

## 任务清单

- [ ] 创建 FastAPI 项目目录结构
  ```
  ai-service/
  ├── app/
  │   ├── api/
  │   ├── core/
  │   ├── models/
  │   └── config.py
  ├── main.py
  └── requirements.txt
  ```
- [ ] 创建 requirements.txt
  ```
  fastapi==0.115.0
  uvicorn[standard]==0.30.0
  httpx==0.27.0
  langchain==0.3.0
  langchain-openai==0.2.0
  networkx==3.3
  pdfplumber==0.11.0
  python-docx==1.1.0
  pydantic==2.9.0
  python-dotenv==1.0.1
  ```
- [ ] 创建 main.py（FastAPI app + lifespan 钩子）
- [ ] 创建 config.py（DeepSeek endpoint/key 配置，从环境变量读取）
- [ ] 创建 app/api/health.py → GET /ai/health 返回 {"status": "ok"}
- [ ] 创建 .env 文件（DEEPSEEK_API_KEY=xxx, DEEPSEEK_BASE_URL=https://api.deepseek.com）
- [ ] 验证：`uvicorn main:app --host 0.0.0.0 --port 8000` 启动正常
- [ ] 验证：`curl http://localhost:8000/ai/health` 返回正常

---

## 验收标准

- [ ] `pip install -r requirements.txt` 无报错
- [ ] uvicorn 启动无报错
- [ ] GET /ai/health 返回 {"status": "ok"}
