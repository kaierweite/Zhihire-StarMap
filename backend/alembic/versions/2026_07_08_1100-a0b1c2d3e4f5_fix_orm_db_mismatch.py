"""fix_orm_db_mismatch

Add columns missing from DB but present in ORM entities:
- match_result.is_stale
- recommend_record.recommend_type
- recommend_record.resume_id (FK to resume.id)

Revision ID: a0b1c2d3e4f5
Revises: z7a8b9c0d1e2
Create Date: 2026-07-08 11:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a0b1c2d3e4f5"
down_revision: Union[str, None] = "z7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_stale to match_result
    op.add_column(
        "match_result",
        sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    # Add recommend_type to recommend_record
    op.add_column(
        "recommend_record",
        sa.Column("recommend_type", sa.String(10), nullable=False, server_default=sa.text("'JOB'")),
    )
    # Add resume_id to recommend_record (FK to resume.id)
    op.add_column(
        "recommend_record",
        sa.Column("resume_id", sa.BigInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("recommend_record", "resume_id")
    op.drop_column("recommend_record", "recommend_type")
    op.drop_column("match_result", "is_stale")
