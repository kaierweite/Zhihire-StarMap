"""day11_register_operation_log

Register operation_log entity in Base.metadata.
Table already exists in DB (01_schema.sql), migration is a no-op stamp.

Revision ID: a1b2c3d4e5f6
Revises: z7a8b9c0d1e2
Create Date: 2026-07-08 11:30:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "1a2b3c4d5e6f"
down_revision: Union[str, None] = "z7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Table already exists in DB via 01_schema.sql
    # This migration only registers the entity in metadata for Alembic tracking
    pass


def downgrade() -> None:
    pass
