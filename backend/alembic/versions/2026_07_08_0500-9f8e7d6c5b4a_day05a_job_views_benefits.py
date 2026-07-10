"""Day migration no-op stamp.

Tables/columns already exist in DB via 01_schema.sql.
This migration is a no-op stamp to register the revision chain.

Revision ID: 9f8e7d6c5b4a
Revises: 0ec0a06ad127
Create Date: 2026-07-08 05:00:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "9f8e7d6c5b4a"
down_revision: Union[str, None] = "0ec0a06ad127"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass