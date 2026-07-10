"""Self-contained resume integration test.
Starts its own server, runs all steps.
"""
import asyncio, json, os, sys, threading, time

# Fix Windows event loop before anything else
# Add project backend dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import httpx, uvicorn

PORT = 17801
BASE = f"http://127.0.0.1:{PORT}/api"
DOCX = os.path.join(os.path.dirname(__file__), "test_resume.docx")
USERNAME = f"intg_{int(time.time())}"
PASSWORD = "test1234"

def start_server():
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="error")

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
time.sleep(4)

cli = httpx.Client(timeout=30)
token = resume_id = task_id = None
passed = failed = 0

def check(step, desc, ok_fn):
    global passed, failed
    try:
        result = ok_fn()
        print(f"  [PASS] {step}: {desc}")
        passed += 1
        return result
    except Exception as e:
        print(f"  [FAIL] {step}: {desc} -> {e}")
        failed += 1
        return None

def rpc(method, path, **kw):
    headers = kw.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = getattr(httpx, method)(f"{BASE}{path}", headers=headers, timeout=30, **kw)
    return resp

print("=" * 55)
print(" Resume Integration Test (self-hosted)")
print("=" * 55)

# 1
check("1/9", "Health check", lambda: (
    rpc("get", "/ping").raise_for_status()
))

# 2
check("2/9", "Register user", lambda: (
    rpc("post", "/auth/register", json={"username": USERNAME, "password": PASSWORD, "role": "USER"}).raise_for_status()
))

# 3
r = check("3/9", "Login", lambda: (
    rpc("post", "/auth/login", json={"username": USERNAME, "password": PASSWORD}).json()
))
if r:
    token = r["data"]["token"]

# 4
with open(DOCX, "rb") as f:
    r = check("4/9", "Upload resume", lambda: (
        rpc("post", "/resume/upload", files={"file": ("res.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}).json()
    ))
if r:
    resume_id = r["data"]["resume_id"]
    task_id = r["data"]["task_id"]
    print(f"         resume_id={resume_id} task_id={task_id}")

# 5
def poll_parse():
    for i in range(30):
        time.sleep(2)
        r = rpc("get", f"/parse/task/{task_id}").json()
        s = r["data"]["status"]
        if s in ("SUCCESS", "FAILED"):
            return f"{s} count={r['data']['result'].get('parsed_count')}"
    return "timeout"
check("5/9", "Parse task", poll_parse)

# 6
r = check("6/9", "Resume list", lambda: rpc("get", "/resume").json())
if r:
    recs = r["data"]["records"]
    if recs:
        print(f"         total={r['data']['total']} first={recs[0]['title']} file_name={recs[0].get('file_name')}")

# 7
r = check("7/9", "Resume detail", lambda: rpc("get", f"/resume/{resume_id}").json())
if r:
    p = r["data"].get("parsed") or {}
    print(f"         name={p.get('name')} skills={len(p.get('skills', []) or [])} exp={len(p.get('experience', []) or [])}")

# 8
r = check("8/9", "Edit resume", lambda: (
    rpc("put", f"/resume/{resume_id}",
        json={"title": "Updated", "content_text": json.dumps({"name": "Zhang San (edited)", "education": "Bachelor", "skills": [{"name": "Java"}, {"name": "Python"}], "experience": []})}).json()
))
if r:
    p = r["data"].get("parsed") or {}
    sk = (p.get("skills") or [{}])[0]
    print(f"         name={p.get('name')} skills[0]={sk}")

# 9
check("9/9", "Delete resume", lambda: rpc("delete", f"/resume/{resume_id}").raise_for_status())
r = check("9/9 verify", "List verify deleted", lambda: rpc("get", "/resume").json())
if r:
    ids = [rec["id"] for rec in r["data"]["records"]]
    ok = resume_id not in ids
    print(f"         removed={ok}")


# Graph check after parse
if passed >= 7:
    r = cli.get(f"{BASE}/graph/user", headers={"Authorization": f"Bearer {token}"}).json()
    d = r.get("data", {})
    n = len(d.get("nodes", []))
    e = len(d.get("edges", []))
    g = len(d.get("gap_skills", []))
    print(f"  Graph: {n} nodes, {e} edges, {g} gap")
    if n:
        print(f"    node0: {d['nodes'][0].get('name')}")
    if e:
        print(f"    edge0: {d['edges'][0].get('source')} -> {d['edges'][0].get('target')}")

cli.close()


print("=" * 55)
print(f" Result: {passed} passed, {failed} failed")
print("=" * 55)
