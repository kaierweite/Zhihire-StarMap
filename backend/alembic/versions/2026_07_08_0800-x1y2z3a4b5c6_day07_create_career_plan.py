"""day07_create_career_plan

创建 career_plan 表，存储用户对目标职业角色的规划分析结果。

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
    op.create_table(
        "career_plan",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("target_role", sa.String(100), nullable=False),
        sa.Column("target_role_id", sa.BigInteger(), nullable=False),
        sa.Column("plan_content", sa.Text(), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default=sa.text("'PROACTIVE'")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("career_plan")