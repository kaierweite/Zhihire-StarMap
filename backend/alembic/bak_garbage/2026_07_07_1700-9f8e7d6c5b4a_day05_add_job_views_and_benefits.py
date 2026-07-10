"""day05_add_job_views_and_benefits

Add views (INTEGER, DEFAULT 0) and benefits (JSONB) columns to job table.

Revision ID: 9f8e7d6c5b4a
Revises: 0ec0a06ad127
Create Date: 2026-07-07 17:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "9f8e7d6c5b4a"
down_revision: Union[str, None] = "0ec0a06ad127"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add views column (INTEGER, DEFAULT 0)
    op.add_column(
        "job",
        sa.Column("views", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    # Add benefits column (JSONB, nullable)
    op.add_column(
        "job",
        sa.Column("benefits", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("job", "benefits")
    op.drop_column("job", "views")
