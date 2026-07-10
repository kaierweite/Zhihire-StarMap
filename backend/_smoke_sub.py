import asyncio, sys, time
sys.path.insert(0, r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend")
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi.testclient import TestClient
from app.db.session import async_engine
from app.db import compat  # noqa
from sqlalchemy import text
import app.main as m

client = TestClient(m.app)
suffix = str(int(time.time()))
uname = f"sub_{suffix}"

r = client.post("/api/auth/register", json={"username":uname,"password":"pass123456","role":"USER","email":"t@t.com","phone":"13800001111"})
r = client.post("/api/auth/login", json={"username":uname,"password":"pass123456"})
token = r.json()["data"]["token"]
h = {"Authorization": f"Bearer {token}"}

# PUT 完整档案含子表
r = client.put("/api/user/profile", headers=h, json={
    "real_name":"李七","gender":"MALE","education":"硕士",
    "school":"南京大学","major":"计算机","current_city":"南京",
    "expected_city":"上海","expected_position":"算法工程师","expected_worktype":"全职","expected_industry":"互联网",
    "expected_salary_min":25,"expected_salary_max":45,
    "bio":"NLP 方向",
    "skills":["Python","PyTorch"],
    "work_experiences":[
        {"title":"算法实习","company":"字节跳动","period":"2024.06-2024.12","description":"参与 LLM 训练"}
    ],
    "project_experiences":[
        {"name":"智能对话","description":"基于大模型的对话系统"}
    ],
    "languages":[
        {"name":"英语","level":"精通"},
        {"name":"日语","level":"基础"}
    ],
    "certificates":[
        {"name":"CET-6"}
    ]
})
assert r.status_code == 200, r.json()
d = r.json()["data"]
print("PUT ok | completeness:", d["profile_completeness"])
print(f"  salary stored: {d['expected_salary_min']}/{d['expected_salary_max']} | position={d['expected_position']} worktype={d['expected_worktype']} industry={d['expected_industry']}")
print(f"  work: {[w['title'] for w in d['work_experiences']]}")
print(f"  projects: {[p['name'] for p in d['project_experiences']]}")
print(f"  languages: {[l['name'] for l in d['languages']]}")
print(f"  certs: {[c['name'] for c in d['certificates']]}")

# GET 确认持久化
r = client.get("/api/user/profile", headers=h)
d = r.json()["data"]
print("\nGET verify:")
print(f"  salary: {d['expected_salary_min']} | languages: {[l['name'] for l in d['languages']]}")
print(f"  fields: position={d['expected_position']} worktype={d['expected_worktype']} industry={d['expected_industry']}")

# 清理
async def cleanup():
    async with async_engine.begin() as conn:
        rr = await conn.execute(text(f"SELECT id FROM \"user\" WHERE username='{uname}'"))
        uids = [row[0] for row in rr]
        if uids:
            ids = ",".join(str(i) for i in uids)
            await conn.execute(text(f"DELETE FROM user_skill WHERE user_id IN ({ids})"))
            for t in ["user_work_experience","user_project_experience","user_language","user_certificate","user_profile"]:
                await conn.execute(text(f"DELETE FROM {t} WHERE user_id IN ({ids})"))
            await conn.execute(text(f"DELETE FROM \"user\" WHERE id IN ({ids})"))
            print("\ncleaned")
asyncio.run(cleanup())
