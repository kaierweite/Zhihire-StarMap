"""临时：以子进程启动 uvicorn 并通过真实 HTTP 验证 day01 端点，随后关闭。"""
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
import json
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def req(method, path, body=None, token=None, timeout=10):
    url = f"http://127.0.0.1:8000{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if body is not None:
        r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        return -1, {"err": str(e)}


def wait_up(proc, max_wait=20):
    for _ in range(max_wait * 2):
        if proc.poll() is not None:
            return False
        try:
            st, _ = req("GET", "/api/ping")
            if st == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main():
    py = r"D:\Anaconda\envs\starmap\python.exe"
    cwd = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend"
    # 构造干净环境，避免 Path/PATH 键重复导致的启动失败
    env = {}
    for k, v in os.environ.items():
        if k.lower() == "path":
            env["PATH"] = v
        else:
            env[k] = env.get(k, v)
    env["PATH"] = env["PATH"] + os.pathsep + r"D:\Anaconda\envs\starmap"

    proc = subprocess.Popen(
        [py, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=cwd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    passed = []
    try:
        if not wait_up(proc):
            err = proc.stderr.read().decode("utf-8", "ignore")[-2000:]
            print("UVICORN FAILED TO START:\n", err[-1500:])
            return
        print("uvicorn started, pid", proc.pid)

        cases = []
        st, b = req("GET", "/api/ping")
        cases.append(("ping", st == 200 and b.get("data") == "pong", b))

        uid = str(int(time.time() * 1000) % 100000)
        u1 = f"uv_{uid}"
        st, b = req("POST", "/api/auth/register", {
            "username": u1, "password": "secret123", "role": "USER",
            "email": f"{u1}@example.com", "phone": "13000000000",
        })
        cases.append(("register USER", st == 200 and b.get("code") == 200, b))

        st, b = req("POST", "/api/auth/register", {"username": u1, "password": "secret123", "role": "USER"})
        cases.append(("duplicate 409", b.get("code") == 409, b))

        st, b = req("POST", "/api/auth/login", {"username": u1, "password": "wrong"})
        cases.append(("login wrong 400", b.get("code") == 400, b))

        st, b = req("POST", "/api/auth/login", {"username": u1, "password": "secret123"})
        token = (b.get("data") or {}).get("token")
        cases.append(("login ok", b.get("code") == 200 and bool(token), b))

        st, b = req("GET", "/api/auth/me", token=token)
        cases.append(("me ok", st == 200 and b.get("code") == 200 and b["data"]["username"] == u1, b))

        st, b = req("GET", "/api/auth/me")
        cases.append(("me no token 401", st == 401 and b.get("code") == 401, b))

        st, b = req("POST", "/api/auth/register", {
            "username": f"uvc_{uid}", "password": "secret123", "role": "COMPANY",
            "company_name": "智聘科技", "contact_email": "c@example.com",
        })
        cases.append(("register COMPANY", b.get("code") == 200, b))

        st, b = req("POST", "/api/auth/login", {"username": f"uvc_{uid}", "password": "secret123"})
        cases.append(("login COMPANY", b.get("code") == 200 and (b.get("data") or {}).get("role") == "COMPANY", b))

        all_ok = True
        for name, ok, detail in cases:
            mark = "PASS" if ok else "FAIL"
            if not ok:
                all_ok = False
            print(f"[{mark}] {name} http={detail}")
        print("\nUVICORN LIVE RESULT:", "ALL PASS" if all_ok else "FAILED")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
