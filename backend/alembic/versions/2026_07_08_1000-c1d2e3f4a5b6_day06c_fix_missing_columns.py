"""day06c_fix_missing_columns — Add missing entity columns

Add columns that were defined in ORM entities but missing from DB:
- match_result.is_stale (Boolean)
- recommend_record.resume_id (BigInteger, FK)
- recommend_record.recommend_type (VARCHAR(10))

Revision ID: c1d2e3f4a5b6
Revises: x1y2z3a4b5c6
Create Date: 2026-07-08 10:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "x1y2z3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("match_result", sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("recommend_record", sa.Column("resume_id", sa.BigInteger(), sa.ForeignKey("resume.id", ondelete="SET NULL"), nullable=True))
    op.add_column("recommend_record", sa.Column("recommend_type", sa.String(10), nullable=False, server_default=sa.text("JOB")))


def downgrade() -> None:
    op.drop_column("recommend_record", "recommend_type")
    op.drop_column("recommend_record", "resume_id")
    op.drop_column("match_result", "is_stale")
