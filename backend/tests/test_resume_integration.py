"""????????????

???
  1. ??????D:\Anaconda\envs\starmap\python.exe run.py
  2. ??????????D:\Anaconda\envs\starmap\python.exe backend\tests\test_resume_integration.py

??????? ? ?? ? ?? ? ???? ? ???? ? ??/?? ? ?? ? ?? ? ??
"""
import json, sys, time, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import httpx

BASE = os.environ.get("TEST_BASE", "http://127.0.0.1:8000/api")
BASE_URL = os.environ.get("TEST_BASE", "http://127.0.0.1:8000/api")
DOCX_PATH = os.path.join(os.path.dirname(__file__), "test_resume.docx")
USERNAME = f"test_resume_{int(time.time())}"
PASSWORD = "test123456"
token = None
resume_id = None
task_id = None

def log(label, data=None):
    print(f"  [{label}] ", end="")
    if data is not None:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:300])
    else:
        print()

def req(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{BASE_URL}{path}"
    r = kwargs.pop("raw_response", False)
    resp = getattr(httpx, method)(url, headers=headers, timeout=30, **kwargs)
    if r:
        return resp
    return resp.json()

def assert_ok(resp, label):
    assert resp.get("code") == 200, f"{label} failed: {resp}"
    return resp.get("data")

print("=" * 50)
print("?? ?????????")
print("=" * 50)

# 1. ????
print("n[1/9] ????")
r = req("get", "/ping", raw_response=True)
assert r.status_code == 200, f"???: {r.status_code}"
log("OK", {"status": r.status_code})

# 2. ??
print("n[2/9] ????")
r = req("post", "/auth/register", json={"username": USERNAME, "password": PASSWORD, "role": "USER"})
assert_ok(r, "??")
log("OK", {"username": USERNAME})

# 3. ??
print("n[3/9] ???? token")
r = req("post", "/auth/login", json={"username": USERNAME, "password": PASSWORD})
data = assert_ok(r, "??")
token = data["access_token"]
log("OK", {"token": token[:20] + "..."})

# 4. ????
print("n[4/9] ??????")
with open(DOCX_PATH, "rb") as f:
    files = {"file": ("test_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    r = req("post", "/resume/upload", files=files)
data = assert_ok(r, "??")
resume_id = data["resume_id"]
task_id = data["task_id"]
log("OK", {"resume_id": resume_id, "task_id": task_id, "title": data["title"]})

# 5. ??????
print("n[5/9] ???????? 2 ??...")
for i in range(30):
    time.sleep(2)
    r = req("get", f"/parse/task/{task_id}")
    data = r.get("data") or r
    status = data.get("status", "")
    print(f"    ? {i+1} ???: status = {status}")
    if status == "SUCCESS":
        log("OK", {"parsed_count": data.get("result", {}).get("parsed_count")})
        break
    elif status == "FAILED":
        print(f"    [WARN] ????: {data.get('result', {}).get('error', 'unknown')}")
        break
else:
    print("    [WARN] ???????????")

# 6. ????
print("n[6/9] ????")
r = req("get", "/resume?page=1&size=20")
data = assert_ok(r, "??")
records = data.get("records", [])
log("OK", {"total": data["total"], "records_count": len(records)})
if records:
    print(f"    ???: id={records[0]['id']} title={records[0]['title']} file_name={records[0].get('file_name')}")

# 7. ????
print("n[7/9] ????")
r = req("get", f"/resume/{resume_id}")
data = assert_ok(r, "??")
print(f"    title: {data['title']}")
print(f"    status: {data['status']}")
print(f"    file_id: {data['file_id']}")
print(f"    has_parsed: {data.get('parsed') is not None}")
if data.get("parsed"):
    p = data["parsed"]
    print(f"    parsed.name: {p.get('name')}")
    print(f"    parsed.education: {p.get('education')}")
    print(f"    parsed.skills: {p.get('skills')}")
    print(f"    parsed.experience: {len(p.get('experience', []))} ??")
log("OK")

# 8. ????
print("n[8/9] ??????")
update_json = json.dumps({
    "name": "???????",
    "education": "??",
    "skills": [{"name": "Java"}, {"name": "Python"}],
    "experience": [{"company": "????", "title": "?????", "period": "2023-2025", "description": "??????"}],
}, ensure_ascii=False)
r = req("put", f"/resume/{resume_id}", json={"title": "???????", "content_text": update_json})
data = assert_ok(r, "??")
parsed = data.get("parsed", {})
print(f"    title: {data['title']}")
print(f"    parsed.name: {parsed.get('name')}")
print(f"    skills[0]: {parsed.get('skills', [{}])[0]}")
log("OK")

# 9. ?????????
print("n[9/9] ????")
r = req("delete", f"/resume/{resume_id}")
assert_ok(r, "??")
# ???????????
r = req("get", "/resume?page=1&size=50")
data = assert_ok(r, "????")
ids = [rec["id"] for rec in data.get("records", [])]
assert resume_id not in ids, f"????: {resume_id} ?????"
log("OK", {"deleted_id": resume_id})

print("=" * 50)
print("?? ?????????")
print("=" * 50)
