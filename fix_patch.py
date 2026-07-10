import os

MIGRATIONS = {
    "2026_07_08_0600-y1z2x3w4v5u6_day08_interview.py": (
        "y1z2x3w4v5u6", "x1y2z3a4b5c6",
        "Register interview module entities. Tables exist in 01_schema.sql.",
    ),
    "2026_07_08_0610-z7a8b9c0d1e2_day09_notification.py": (
        "z7a8b9c0d1e2", "y1z2x3w4v5u6",
        "Register notification entity. Table exists in 01_schema.sql.",
    ),
    "2026_07_08_0620-b5c6d7e8f9a0_day10_fix_columns.py": (
        "b5c6d7e8f9a0", "z7a8b9c0d1e2",
        "Add missing ORM columns: match_result.is_stale, recommend_record.recommend_type, recommend_record.resume_id.",
    ),
}

def build(rev: str, down: str, desc: str, *, has_sql: bool = False) -> str:
    lines = []
    lines.append('"""' + desc)
    lines.append("")
    lines.append(f"Revision ID: {rev}")
    lines.append(f"Revises: {down}")
    lines.append("Create Date: 2026-07-08 06:00:00.000000+08:00")
    lines.append('"""')
    lines.append("from typing import Sequence, Union")
    lines.append("from alembic import op")
    lines.append("import sqlalchemy as sa")
    lines.append("")
    lines.append(f'revision: str = "{rev}"')
    lines.append(f'down_revision: Union[str, None] = "{down}"')
    lines.append("branch_labels: Union[str, Sequence[str], None] = None")
    lines.append("depends_on: Union[str, Sequence[str], None] = None")
    lines.append("")
    lines.append("def upgrade() -> None:")
    if has_sql:
        lines.append('    op.add_column("match_result",')
        lines.append('        sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),')
        lines.append("    )")
        lines.append('    op.add_column("recommend_record",')
        lines.append('        sa.Column("recommend_type", sa.String(10), nullable=False, server_default=sa.text("\\\'JOB\\\'")),')
        lines.append("    )")
        lines.append('    op.add_column("recommend_record",')
        lines.append('        sa.Column("resume_id", sa.BigInteger(), nullable=True),')
        lines.append("    )")
    else:
        lines.append("    pass")
    lines.append("")
    lines.append("def downgrade() -> None:")
    if has_sql:
        lines.append('    op.drop_column("recommend_record", "resume_id")')
        lines.append('    op.drop_column("recommend_record", "recommend_type")')
        lines.append('    op.drop_column("match_result", "is_stale")')
    else:
        lines.append("    pass")
    return "\n".join(lines)

d = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\alembic\versions"
for fname, (rev, down, desc) in MIGRATIONS.items():
    has_sql = "fix" in fname
    content = build(rev, down, desc, has_sql=has_sql)
    fp = os.path.join(d, fname)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {fname}")
print("Done!")
