# Day 10 — 麒麟虚机部署验证

> **前置依赖**：Day 09（联调通过）

---

## 任务清单

- [ ] 麒麟虚机 Python 环境准备
  - pip install -r requirements.txt
  - 验证所有依赖可安装（networkx/pdfplumber/python-docx）
- [ ] 创建 systemd service 文件
  `
  [Unit]
  Description=StarMap AI Service
  After=network.target
  
  [Service]
  ExecStart=/usr/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
  Restart=always
  
  [Install]
  WantedBy=multi-user.target
  `
- [ ] 启动服务：systemctl start starmap-ai
- [ ] 验证：curl http://localhost:8000/ai/health
- [ ] 全功能验证：后端调 AI 服务跑通
- [ ] 配置 Nginx 反向代理（可选）

---

## 验收标准

- [ ] systemctl status starmap-ai 显示 active (running)
- [ ] GET /ai/health 返回正常
- [ ] 后端调 AI 服务全链路在虚机上通过