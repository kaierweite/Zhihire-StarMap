"""Fix backtick stripping in parse_service.py and resume_service.py."""
import os

base = r"C:\Users\Administrator\Desktop\Zhihire-StarMap"
files = [
    os.path.join(base, "backend", "app", "services", "parse_service.py"),
    os.path.join(base, "backend", "app", "services", "resume_service.py"),
]

for path in files:
    with open(path, "rb") as f:
        data = f.read()

    # Fix startswith: single backtick -> triple backtick
    old_s = b'if clean.startswith("json"):'
    new_s = b'if clean.startswith("`json"):'
    old_e = b'if clean.endswith(""):'
    new_e = b'if clean.endswith("`"):'
    old_raw_s = b'if raw.startswith("json"):'
    new_raw_s = b'if raw.startswith("`json"):'
    old_raw_e = b'if raw.endswith(""):'
    new_raw_e = b'if raw.endswith("`"):'

    changed = False
    if old_s in data:
        data = data.replace(old_s, new_s)
        changed = True
        print(f"  Fixed startswith in {os.path.basename(path)}")
    if old_e in data:
        data = data.replace(old_e, new_e)
        changed = True
        print(f"  Fixed endswith in {os.path.basename(path)}")
    if old_raw_s in data:
        data = data.replace(old_raw_s, new_raw_s)
        changed = True
        print(f"  Fixed raw.startswith in {os.path.basename(path)}")
    if old_raw_e in data:
        data = data.replace(old_raw_e, new_raw_e)
        changed = True
        print(f"  Fixed raw.endswith in {os.path.basename(path)}")

    if changed:
        with open(path, "wb") as f:
            f.write(data)
        print(f"  [OK] {os.path.basename(path)}")
    else:
        print(f"  [SKIP] {os.path.basename(path)} (already fixed)")