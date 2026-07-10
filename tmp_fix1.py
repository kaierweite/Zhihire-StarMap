import sys
sys.stdout.reconfigure(encoding="utf-8")

path = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\models\schemas\company.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Strip leading space from lines 3-8 (0-indexed: lines 2-7)
fixed = []
for i, line in enumerate(lines):
    if 2 <= i <= 7 and line.startswith(" "):
        fixed.append(line[1:])
    else:
        fixed.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(fixed)

print("Fixed leading spaces in company.py")
