"""Register notification entity. Table exists in 01_schema.sql.

Revision ID: z7a8b9c0d1e2
Revises: y1z2x3w4v5u6
Create Date: 2026-07-08 06:00:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "z7a8b9c0d1e2"
down_revision: Union[str, None] = "y1z2x3w4v5u6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass