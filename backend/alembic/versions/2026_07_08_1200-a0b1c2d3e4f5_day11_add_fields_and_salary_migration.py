"""day11: add is_campus to job, company_type to company, migrate salary to yuan.

Revision ID: a0b1c2d3e4f5
Revises: b5c6d7e8f9a0
Create Date: 2026-07-08 12:00:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a0b1c2d3e4f5'
down_revision: Union[str, None] = 'b5c6d7e8f9a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_campus to job table
    op.add_column('job', sa.Column('is_campus', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    # Add company_type to company table
    op.add_column('company', sa.Column('company_type', sa.String(50), nullable=True))
    # Migrate salary from K to yuan (multiply by 1000)
    op.execute('UPDATE job SET salary_min = salary_min * 1000 WHERE salary_min IS NOT NULL')
    op.execute('UPDATE job SET salary_max = salary_max * 1000 WHERE salary_max IS NOT NULL')


def downgrade() -> None:
    op.execute('UPDATE job SET salary_min = salary_min / 1000 WHERE salary_min IS NOT NULL')
    op.execute('UPDATE job SET salary_max = salary_max / 1000 WHERE salary_max IS NOT NULL')
    op.drop_column('company', 'company_type')
    op.drop_column('job', 'is_campus')