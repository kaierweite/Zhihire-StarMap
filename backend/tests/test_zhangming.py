"""Test ??.docx upload + parse + detail flow."""
import asyncio, sys, time, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import threading, uvicorn
from app.main import app

PORT = 8101
BASE = f"http://127.0.0.1:{PORT}/api"
DOCX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "??.docx")

def start():
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="error")

t = threading.Thread(target=start, daemon=True)
t.start()
time.sleep(4)

import httpx
cli = httpx.Client(timeout=30)

print('=== Test ??.docx ===')

# 1. Register + login
cli.post(f"{BASE}/auth/register", json={"username": "zm_test", "password": "test1234", "role": "USER"})
r = cli.post(f"{BASE}/auth/login", json={"username": "zm_test", "password": "test1234"}).json()
token = r["data"]["token"]
print(f"[1] Login OK, token={token[:20]}...")

# 2. Upload
with open(DOCX, 'rb') as f:
    r = cli.post(f"{BASE}/resume/upload",
        files={"file": ("zhangming.docx", f,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers={"Authorization": f"Bearer {token}"}).json()
rid = r["data"]["resume_id"]
tid = r["data"]["task_id"]
print(f"[2] Upload OK, resume_id={rid} task_id={tid}")

# 3. Poll
for i in range(30):
    time.sleep(2)
    r = cli.get(f"{BASE}/parse/task/{tid}", headers={"Authorization": f"Bearer {token}"}).json()
    s = r["data"]["status"]
    print(f"  Poll {i+1}: {s}")
    if s in ("SUCCESS", "FAILED"):
        print(f"[3] Parse: {s}")
        if s == "FAILED":
            print(f"  Error: {r["data"]["result"]}")
        break

# 4. Detail
r = cli.get(f"{BASE}/resume/{rid}", headers={"Authorization": f"Bearer {token}"}).json()
d = r["data"]
p = d.get("parsed")
ct = d.get("content_text", "")
print(f"[4] Detail:")
print(f"  title: {d.get('title')}")
print(f"  parsed is None: {p is None}")
if p:
    print(f"  name: {p.get('name')}")
    print(f"  education: {p.get('education')}")
    print(f"  skills: {p.get('skills')}")
    print(f"  experience: {len(p.get('experience', []) or [])} items")
else:
    print(f"  content_text[:400]: {ct[:400]}")

cli.close()
print("=== Done ===")