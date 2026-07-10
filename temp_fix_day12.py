fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\alembic\versions\2026_07_08_1230-c1d2e3f4a5b6_day12_add_major_and_job_category.py'
with open(fp, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("down_revision: Union[str, None] = 'a0b1c2d3e4f5'", "down_revision: Union[str, None] = 'e31fd1187d63'")
with open(fp, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated')