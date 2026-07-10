import json, sys, os, time, httpx

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8000/api"
cli = httpx.Client(timeout=30)

# 1. Login
r = cli.post(f"{BASE}/auth/login", json={"username": "zm", "password": "test1234"}).json()
token = r["data"]["token"]
print(f"[1] Login OK")

# 2. Upload ??.docx
with open(r"C:\Users\Administrator\Desktop\Zhihire-StarMap\??.docx", "rb") as f:
    r = cli.post(f"{BASE}/resume/upload",
        files={"file": ("??.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers={"Authorization": f"Bearer {token}"}).json()
rid = r["data"]["resume_id"]
tid = r["data"]["task_id"]
print(f"[2] Upload OK: resume={rid} task={tid}")

# 3. Poll
for i in range(30):
    time.sleep(2)
    r = cli.get(f"{BASE}/parse/task/{tid}", headers={"Authorization": f"Bearer {token}"}).json()
    s = r["data"]["status"]
    print(f"  Poll {i+1}: {s}")
    if s in ("SUCCESS", "FAILED"):
        print(f"[3] Parse: {s}")
        break

# 4. Detail
r = cli.get(f"{BASE}/resume/{rid}", headers={"Authorization": f"Bearer {token}"}).json()
d = r["data"]
p = d.get("parsed")
print(f"[4] Detail:")
print(f"  title: {d.get('title')}")
print(f"  parsed is None: {p is None}")
if p:
    for k in ['name','education','years','targetJob','city']:
        print(f"  {k}: {p.get(k)}")
    sk = p.get('skills')
    print(f"  skills: {sk}")
    ex = p.get('experience')
    print(f"  experience: {len(ex) if ex else 0} items")
    print(f"  raw_response present: {'raw_response' in p}")
else:
    print(f"  content_text[:500]: {d.get('content_text','')[:500]}")

cli.close()
print("[5] Done")