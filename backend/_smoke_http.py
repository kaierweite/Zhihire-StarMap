"""Day02 HTTP 冒烟测试：启动后台应用并用 TestClient 验证完整登录->档案流程。"""
import asyncio
import sys
import time

sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")

# Windows psycopg 需要 SelectorEventLoop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi.testclient import TestClient
from app.db import compat  # noqa: F401
import app.main as m

client = TestClient(m.app)

suffix = f"ht{int(time.time())}"
username = f"test_{suffix}"

# 注册
r = client.post("/api/auth/register", json={
    "username": username, "password": "pass123456",
    "role": "USER", "email": f"{username}@ex.com", "phone": "13800000000",
})
print("register:", r.status_code, r.json())

# 登录
r = client.post("/api/auth/login", json={"username": username, "password": "pass123456"})
print("login:", r.status_code, r.json())
token = r.json()["data"]["token"]
h = {"Authorization": f"Bearer {token}"}

# GET profile（首访自动建空档案）
r = client.get("/api/user/profile", headers=h)
print("GET profile1:", r.status_code, r.json()["code"], r.json()["data"]["profile_completeness"], "skills", len(r.json()["data"]["skills"]))

# PUT profile
r = client.put("/api/user/profile", headers=h, json={
    "real_name": "李四", "gender": "FEMALE", "education": "硕士",
    "school": "北京大学", "major": "软件工程", "current_city": "北京",
    "expected_city": "北京", "expected_salary_min": 20000, "expected_salary_max": 35000,
    "bio": "全栈工程师", "skills": ["Vue.js", "springboot", "新候选技能ABC"],
})
print("PUT profile:", r.status_code, r.json()["code"], "completeness", r.json()["data"]["profile_completeness"])
print("  skills:", [s["name"] for s in r.json()["data"]["skills"]])

# GET profile 确认持久化
r = client.get("/api/user/profile", headers=h)
print("GET profile2:", r.status_code, r.json()["code"], "completeness", r.json()["data"]["profile_completeness"], "skills", [s["name"] for s in r.json()["data"]["skills"]])

# 无 token -> 401
r = client.get("/api/user/profile")
print("no token:", r.status_code, r.json()["code"], r.json()["message"])
