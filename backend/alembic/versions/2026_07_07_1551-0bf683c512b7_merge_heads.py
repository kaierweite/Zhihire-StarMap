"""merge_heads

Revision ID: 0bf683c512b7
Revises: 848a3822073a, c6d5e4f3a2b1
Create Date: 2026-07-07 15:51:22.652917+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bf683c512b7'
down_revision: Union[str, None] = ('848a3822073a', 'c6d5e4f3a2b1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass