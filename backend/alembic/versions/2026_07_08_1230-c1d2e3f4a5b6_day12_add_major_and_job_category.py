"""day12: add major and job_category columns to job table.

Revision ID: c1d2e3f4a5b6
Revises: a0b1c2d3e4f5
Create Date: 2026-07-08 12:30:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'a0b1c2d3e4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('job', sa.Column('major', sa.String(200), nullable=True))
    op.add_column('job', sa.Column('job_category', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('job', 'job_category')
    op.drop_column('job', 'major')
