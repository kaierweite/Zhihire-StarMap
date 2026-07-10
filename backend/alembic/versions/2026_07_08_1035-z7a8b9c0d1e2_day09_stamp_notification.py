"""day09_stamp_notification

Register notification entity in Base.metadata.
Table already exists in DB (01_schema.sql), migration is a no-op stamp.

Revision ID: z7a8b9c0d1e2
Revises: y1z2x3w4v5u6
Create Date: 2026-07-08 10:35:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "z7a8b9c0d1e2"
down_revision: Union[str, None] = "y1z2x3w4v5u6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Table already exists in DB via 01_schema.sql
    # This migration only registers the entity in metadata for Alembic tracking
    pass


def downgrade() -> None:
    pass
