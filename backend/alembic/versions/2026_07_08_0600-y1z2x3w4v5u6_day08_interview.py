"""Register interview module entities. Tables exist in 01_schema.sql.

Revision ID: y1z2x3w4v5u6
Revises: x1y2z3a4b5c6
Create Date: 2026-07-08 06:00:00.000000+08:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "y1z2x3w4v5u6"
down_revision: Union[str, None] = "x1y2z3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass