"""add major and job_category columns to job.

Revision ID: 4866ad7374ed
Revises: cdd9ea314360
Create Date: 2026-07-08 18:22:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '4866ad7374ed'
down_revision: Union[str, None] = 'cdd9ea314360'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('job', sa.Column('major', sa.String(200), nullable=True))
    op.add_column('job', sa.Column('job_category', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('job', 'job_category')
    op.drop_column('job', 'major')
