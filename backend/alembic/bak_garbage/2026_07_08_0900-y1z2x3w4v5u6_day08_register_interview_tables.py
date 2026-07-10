"""day08_register_interview_tables

Register 5 interview module entities into Base.metadata.
Tables already exist in DB (01_schema.sql), migration is a no-op stamp.

Revision ID: y1z2x3w4v5u6
Revises: x1y2z3a4b5c6
Create Date: 2026-07-08 09:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "y1z2x3w4v5u6"
down_revision: Union[str, None] = "x1y2z3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables already exist in DB via 01_schema.sql
    # This migration only registers entities in metadata for Alembic tracking
    pass


def downgrade() -> None:
    pass
