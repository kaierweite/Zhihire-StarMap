import py_compile, os

d = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend"
files = [
    os.path.join(d, "app", "services", "match_service.py"),
    os.path.join(d, "app", "services", "job_service.py"),
    os.path.join(d, "app", "api", "v1", "job.py"),
    os.path.join(d, "app", "models", "schemas", "job.py"),
    os.path.join(d, "app", "repositories", "job_application_repository.py"),
]
ok = True
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        dirname = os.path.basename(os.path.dirname(f))
        print(f"  OK: {dirname}/{os.path.basename(f)}")
    except py_compile.PyCompileError as e:
        print(f"  FAIL: {f} -> {e}")
        ok = False
if ok:
    print("All files compile successfully.")
else:
    exit(1)
