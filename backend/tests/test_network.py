"""Test network connectivity to DeepSeek API."""
import urllib.request, json

print("Test 1: jsonplaceholder (general HTTPS)")
try:
    r = urllib.request.urlopen("https://jsonplaceholder.typicode.com/todos/1", timeout=5)
    print(f"  OK: {r.status}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")

print()
print("Test 2: api.deepseek.com")
req = urllib.request.Request(
    "https://api.deepseek.com/v1/chat/completions",
    data=json.dumps({"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}).encode(),
    headers={"Content-Type":"application/json","Authorization":"Bearer sk-ec9e86043ab84ec3b5b2def1d37b1958"},
    method="POST")
try:
    r = urllib.request.urlopen(req, timeout=10)
    print(f"  OK: {r.status}")
    body = r.read().decode()[:300]
    print(f"  Body: {body}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")
