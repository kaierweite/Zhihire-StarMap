"""day05_add_job_application_table

Create job_application table for resume delivery feature.

Revision ID: f7e8d9c0b1a2
Revises: 9f8e7d6c5b4a
Create Date: 2026-07-07 17:30:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f7e8d9c0b1a2"
down_revision: Union[str, None] = "9f8e7d6c5b4a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_application",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("job_id", sa.BigInteger(), sa.ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("resume_id", sa.BigInteger(), sa.ForeignKey("resume.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'APPLIED'")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("job_application")
