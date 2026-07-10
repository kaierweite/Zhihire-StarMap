"""day07_create_career_plan

创建 career_plan 表（初始 schema SQL 已建，不重建），
添加 target_role_id 列。

Revision ID: x1y2z3a4b5c6
Revises: b0c1d2e3f4a5
Create Date: 2026-07-08 08:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "x1y2z3a4b5c6"
down_revision: Union[str, None] = "b0c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # career_plan 表已由 01_schema.sql 创建，仅补缺列
    op.add_column(
        "career_plan",
        sa.Column("target_role_id", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
    )


def downgrade() -> None:
    op.drop_column("career_plan", "target_role_id")