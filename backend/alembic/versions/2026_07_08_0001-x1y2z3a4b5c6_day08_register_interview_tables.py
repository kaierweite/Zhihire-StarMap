"""day08_register_interview_tables — phantom migration placeholder

This migration exists only to fix the Alembic revision chain.
It is a no-op since the tables already exist in the database.

Revision ID: x1y2z3a4b5c6
Revises: y1z2x3w4v5u6
Create Date: 2026-07-08 00:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "x1y2z3a4b5c6"
down_revision: Union[str, None] = "y1z2x3w4v5u6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
