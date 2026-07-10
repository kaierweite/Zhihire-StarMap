import os

FILES = {
    "2026_07_08_0500-9f8e7d6c5b4a_day05a_job_views_benefits.py": ("9f8e7d6c5b4a", "0ec0a06ad127"),
    "2026_07_08_0510-f7e8d9c0b1a2_day05b_job_application.py": ("f7e8d9c0b1a2", "9f8e7d6c5b4a"),
    "2026_07_08_0520-a9b8c7d6e5f4_day06a_match_recommend.py": ("a9b8c7d6e5f4", "f7e8d9c0b1a2"),
    "2026_07_08_0530-b0c1d2e3f4a5_day06b_match_fields.py": ("b0c1d2e3f4a5", "a9b8c7d6e5f4"),
    "2026_07_08_0540-x1y2z3a4b5c6_day07_career_plan.py": ("x1y2z3a4b5c6", "b0c1d2e3f4a5"),
}

def build(rev: str, down: str) -> str:
    lines = [
        '"""Day migration no-op stamp.',
        "",
        "Tables/columns already exist in DB via 01_schema.sql.",
        "This migration is a no-op stamp to register the revision chain.",
        "",
        f"Revision ID: {rev}",
        f"Revises: {down}",
        'Create Date: 2026-07-08 05:00:00.000000+08:00',
        '"""',
        "from typing import Sequence, Union",
        "from alembic import op",
        "import sqlalchemy as sa",
        "",
        f'revision: str = "{rev}"',
        f'down_revision: Union[str, None] = "{down}"',
        "branch_labels: Union[str, Sequence[str], None] = None",
        "depends_on: Union[str, Sequence[str], None] = None",
        "",
        "def upgrade() -> None:",
        "    pass",
        "",
        "def downgrade() -> None:",
        "    pass",
    ]
    return "\n".join(lines)

d = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\alembic\versions"
for fname, (rev, down) in FILES.items():
    fp = os.path.join(d, fname)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(build(rev, down))
    print(f"Created: {fname}")
print("Done!")
