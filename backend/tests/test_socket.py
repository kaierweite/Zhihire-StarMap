"""Test raw socket + SSL connectivity."""
import socket, ssl

print("Test 1: raw socket to 117.187.145.176:443")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(("117.187.145.176", 443))
    s.close()
    print("  OK")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")

print("Test 2: SSL socket to api.deepseek.com:443")
try:
    ctx = ssl.create_default_context()
    s = socket.create_connection(("api.deepseek.com", 443), timeout=5)
    ss = ctx.wrap_socket(s, server_hostname="api.deepseek.com")
    print(f"  OK: {ss.version()}")
    ss.close()
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")

print("Test 3: raw socket to jsonplaceholder:443")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    addr = socket.getaddrinfo("jsonplaceholder.typicode.com", 443)[0][4][0]
    s.connect((addr, 443))
    s.close()
    print("  OK")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")

print("Done")
