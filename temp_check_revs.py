import os
d = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\alembic\versions'
for f in sorted(os.listdir(d)):
    if not f.endswith('.py') or '__pycache__' in f:
        continue
    fp = os.path.join(d, f)
    with open(fp, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    rev = ''
    down = ''
    for line in lines:
        if 'revision:' in line and 'str =' in line:
            rev = line.split("'")[1] if "'" in line else ''
        if 'down_revision:' in line and 'None' not in line:
            down_parts = line.split("'")
            if len(down_parts) > 1:
                down = down_parts[1]
    print(f'{f[:55]:55s} rev={rev}  down={down}')