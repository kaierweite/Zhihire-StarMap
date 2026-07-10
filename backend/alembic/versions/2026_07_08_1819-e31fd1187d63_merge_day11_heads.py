"""merge_day11_heads

Revision ID: e31fd1187d63
Revises: c1d2e3f4a5b6, b2c3d4e5f6a7
Create Date: 2026-07-08 18:19:56.100150+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e31fd1187d63'
down_revision: Union[str, None] = ('c1d2e3f4a5b6', 'b2c3d4e5f6a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass