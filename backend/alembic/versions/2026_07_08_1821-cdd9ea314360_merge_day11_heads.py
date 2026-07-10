"""merge_day11_heads

Revision ID: cdd9ea314360
Revises: a0b1c2d3e4f5, b2c3d4e5f6a7
Create Date: 2026-07-08 18:21:51.159333+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdd9ea314360'
down_revision: Union[str, None] = ('a0b1c2d3e4f5', 'b2c3d4e5f6a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass