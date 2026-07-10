"""day01 认证模块端到端冒烟验证（TestClient，无需启动 uvicorn）。"""
import asyncio
import sys

# Windows + psycopg async 必须使用 SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ok = True


def check(name, cond, detail=""):
    global ok
    mark = "PASS" if cond else "FAIL"
    if not cond:
        ok = False
    print(f"[{mark}] {name} {detail}")


def main():
    uid = str(int(asyncio.get_event_loop().time() * 1000) % 100000)
    uname_user = f"smoke_user_{uid}"
    uname_comp = f"smoke_comp_{uid}"

    # 1. ping
    r = client.get("/api/ping")
    body = r.json()
    check("ping", r.status_code == 200 and body.get("data") == "pong", str(body))

    # 2. 注册求职者
    r = client.post(
        "/api/auth/register",
        json={
            "username": uname_user,
            "password": "secret123",
            "role": "USER",
            "email": "u@example.com",
            "phone": "13800000000",
        },
    )
    body = r.json()
    check("register USER", r.status_code == 200 and body.get("code") == 200, str(body))

    # 3. 重复用户名 -> 409
    r = client.post(
        "/api/auth/register",
        json={"username": uname_user, "password": "secret123", "role": "USER"},
    )
    body = r.json()
    check("duplicate username 409", body.get("code") == 409, str(body))

    # 4. 注册时禁止 ADMIN
    r = client.post(
        "/api/auth/register",
        json={"username": f"adm_{uid}", "password": "secret123", "role": "ADMIN"},
    )
    body = r.json()
    check("register ADMIN rejected", r.status_code == 422 or body.get("code") != 200, str(body))

    # 5. 登录密码错误 -> 400
    r = client.post(
        "/api/auth/login",
        json={"username": uname_user, "password": "wrongpass"},
    )
    body = r.json()
    check("login wrong password 400", body.get("code") == 400, str(body))

    # 6. 登录正确 -> 返回 token/role/username
    r = client.post(
        "/api/auth/login",
        json={"username": uname_user, "password": "secret123"},
    )
    body = r.json()
    token = (body.get("data") or {}).get("token")
    check(
        "login success",
        body.get("code") == 200 and bool(token) and body["data"]["role"] == "USER",
        str(body),
    )

    # 7. GET /api/auth/me 带 token
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    body = r.json()
    check(
        "me with token",
        r.status_code == 200
        and body.get("code") == 200
        and body["data"]["username"] == uname_user
        and body["data"]["role"] == "USER",
        str(body),
    )

    # 8. GET /api/auth/me 无 token -> 401
    r = client.get("/api/auth/me")
    body = r.json()
    check("me without token 401", r.status_code == 401 and body.get("code") == 401, str(body))

    # 9. 注册企业 -> 同时建企业记录
    r = client.post(
        "/api/auth/register",
        json={
            "username": uname_comp,
            "password": "secret123",
            "role": "COMPANY",
            "company_name": "智聘科技",
            "contact_email": "c@example.com",
            "contact_phone": "13900000000",
        },
    )
    body = r.json()
    check("register COMPANY", body.get("code") == 200, str(body))

    # 10. 企业登录 -> role COMPANY
    r = client.post(
        "/api/auth/login",
        json={"username": uname_comp, "password": "secret123"},
    )
    body = r.json()
    check(
        "login COMPANY role",
        body.get("code") == 200 and body.get("data", {}).get("role") == "COMPANY",
        str(body),
    )

    # 11. 企业缺少 company_name -> 400
    r = client.post(
        "/api/auth/register",
        json={"username": f"comp_bad_{uid}", "password": "secret123", "role": "COMPANY"},
    )
    body = r.json()
    check("company without name 400", body.get("code") == 400, str(body))

    print("\nRESULT:", "ALL PASS" if ok else "SOME FAILED")


if __name__ == "__main__":
    main()
