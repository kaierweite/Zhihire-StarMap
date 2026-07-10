"""day06_add_match_and_recommend_tables

Create match_result and recommend_record tables for matching & recommendation feature.

Revision ID: a9b8c7d6e5f4
Revises: f7e8d9c0b1a2
Create Date: 2026-07-07 18:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, None] = "f7e8d9c0b1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "match_result",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("resume_id", sa.BigInteger(), sa.ForeignKey("resume.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("job_id", sa.BigInteger(), sa.ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("match_detail", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'\''0'\''::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recommend_record",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("job_id", sa.BigInteger(), sa.ForeignKey("job.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_clicked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_invited", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'\''0'\''::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("recommend_record")
    op.drop_table("match_result")
