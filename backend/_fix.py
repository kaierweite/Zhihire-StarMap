import io

p = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\services\user_service.py"

with io.open(p, encoding="utf-8") as f:
    t = f.read()

old = (
    "    # 技能section：全量替换\n"
    '    has_skills = bool(rows_for_skills) if "rows_for_skills" in dir() else False\n'
    "    if form.skills is not None:\n"
    "        has_skills = await _replace_user_skills(db, user.id, form.skills)\n"
)

new = (
    "    # 技能section：全量替换（未提供 skills 时不改动；has_skills 沿用当前是否有关联）\n"
    "    has_skills = len(await user_skill_repository.list_active_skill_ids(db, user.id)) > 0\n"
    "    if form.skills is not None:\n"
    "        has_skills = await _replace_user_skills(db, user.id, form.skills)\n"
)

assert old in t, "old block not found"
t = t.replace(old, new)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(t)

print("ok")
