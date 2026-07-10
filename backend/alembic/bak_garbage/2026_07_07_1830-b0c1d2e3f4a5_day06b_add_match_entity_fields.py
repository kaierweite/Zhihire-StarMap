"""day06b_add_match_entity_fields

Add is_stale to match_result, resume_id + recommend_type to recommend_record.

Revision ID: b0c1d2e3f4a5
Revises: a9b8c7d6e5f4
Create Date: 2026-07-07 18:30:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b0c1d2e3f4a5"
down_revision: Union[str, None] = "a9b8c7d6e5f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("match_result", sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("recommend_record", sa.Column("resume_id", sa.BigInteger(), sa.ForeignKey("resume.id", ondelete="SET NULL"), nullable=True))
    op.add_column("recommend_record", sa.Column("recommend_type", sa.String(10), nullable=False, server_default=sa.text("'\''JOB'\''")))


def downgrade() -> None:
    op.drop_column("recommend_record", "recommend_type")
    op.drop_column("recommend_record", "resume_id")
    op.drop_column("match_result", "is_stale")
