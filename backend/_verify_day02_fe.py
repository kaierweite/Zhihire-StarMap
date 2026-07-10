import asyncio, sys
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi.testclient import TestClient
from app.db import compat  # noqa
import app.main as m

client = TestClient(m.app)

# 注册新用户
import time
suffix = str(int(time.time()))
uname = f"ft_{suffix}"
r = client.post("/api/auth/register", json={
    "username": uname, "password": "pass123456", "role": "USER",
    "email": f"{uname}@t.com", "phone": "13800001111",
})
assert r.json()["code"] == 200, f"register fail: {r.json()}"

r = client.post("/api/auth/login", json={"username": uname, "password": "pass123456"})
assert r.json()["code"] == 200
token = r.json()["data"]["token"]
h = {"Authorization": f"Bearer {token}"}

# GET profile - 首访空档案
r = client.get("/api/user/profile", headers=h)
assert r.json()["code"] == 200, f"get fail: {r.json()}"
d = r.json()["data"]
print("GET 首访:", d["profile_completeness"], d["real_name"], d["current_city"], len(d["skills"]))

# PUT profile - 填写完整档案
r = client.put("/api/user/profile", headers=h, json={
    "real_name": "赵六", "gender": "MALE", "education": "本科",
    "school": "清华大学", "major": "计算机",
    "current_city": "北京", "expected_city": "上海",
    "expected_salary_min": 20000, "expected_salary_max": 40000,
    "bio": "资深全栈工程师",
    "skills": ["Vue 3", "Python", "Go", "Node.js", "Docker"],
})
assert r.json()["code"] == 200, f"put fail: {r.json()}"
d = r.json()["data"]
print("PUT 填写后:", d["profile_completeness"], d["real_name"], d["current_city"])
print("  skills:", [s["name"] for s in d["skills"]])

# GET 二次确认
r = client.get("/api/user/profile", headers=h)
d = r.json()["data"]
print("GET 二次确认:", d["profile_completeness"], "skills:", [s["name"] for s in d["skills"]])

# 清理测试数据
from sqlalchemy import text
from app.db.session import async_engine
async def cleanup():
    async with async_engine.begin() as conn:
        r2 = await conn.execute(text(f"SELECT id FROM \"user\" WHERE username='{uname}'"))
        uids = [row[0] for row in r2]
        if uids:
            ids = ",".join(str(i) for i in uids)
            await conn.execute(text(f"DELETE FROM user_skill WHERE user_id IN ({ids})"))
            await conn.execute(text(f"DELETE FROM user_profile WHERE user_id IN ({ids})"))
            await conn.execute(text(f"DELETE FROM \"user\" WHERE id IN ({ids})"))
            print("cleaned test user")
        # 删除候选技能
        for cand in ["Vue 3", "Node.js"]:
            rx = await conn.execute(text(f"SELECT id FROM skill WHERE name='{cand}' AND status='CANDIDATE'"))
            for row in rx:
                await conn.execute(text(f"DELETE FROM skill_synonym WHERE skill_id={row[0]}"))
                await conn.execute(text(f"DELETE FROM skill WHERE id={row[0]}"))
                print(f"cleaned candidate skill: {cand}")
asyncio.run(cleanup())
