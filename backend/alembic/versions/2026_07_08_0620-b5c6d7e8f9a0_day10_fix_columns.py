"""Add missing ORM columns: match_result.is_stale, recommend_record.recommend_type, recommend_record.resume_id.

Revision ID: b5c6d7e8f9a0
Revises: z7a8b9c0d1e2
Create Date: 2026-07-08 06:00:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b5c6d7e8f9a0"
down_revision: Union[str, None] = "z7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("match_result",
        sa.Column("is_stale", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("recommend_record",
        sa.Column("recommend_type", sa.String(10), nullable=False, server_default=sa.text("\'JOB\'")),
    )
    op.add_column("recommend_record",
        sa.Column("resume_id", sa.BigInteger(), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("recommend_record", "resume_id")
    op.drop_column("recommend_record", "recommend_type")
    op.drop_column("match_result", "is_stale")