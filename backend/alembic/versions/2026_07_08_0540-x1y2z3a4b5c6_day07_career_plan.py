"""Day migration no-op stamp.

Tables/columns already exist in DB via 01_schema.sql.
This migration is a no-op stamp to register the revision chain.

Revision ID: x1y2z3a4b5c6
Revises: b0c1d2e3f4a5
Create Date: 2026-07-08 05:00:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "x1y2z3a4b5c6"
down_revision: Union[str, None] = "b0c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass