import io
p = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\alembic\versions\2026_07_07_1130-c6d5e4f3a2b1_create_profile_sub_tables.py"
t = io.open(p, encoding="utf-8").read()
# 移除 4 个 create_index 调用
for suffix in ["user_work_experience", "user_project_experience", "user_language", "user_certificate"]:
    old = f'    op.create_index(op.f("ix_{suffix}_user_id"), "{suffix}", ["user_id"])\n'
    t = t.replace(old, "")
# 更新 downgrade 也移除对应 drop_index
for suffix in ["user_certificate", "user_language", "user_project_experience", "user_work_experience"]:
    old = f'    op.drop_index(op.f("ix_{suffix}_user_id"), table_name="{suffix}")\n'
    t = t.replace(old, "")
io.open(p, "w", encoding="utf-8").write(t)
print("ok")
