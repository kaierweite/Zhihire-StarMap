mig_content = '''\"\"\"add major and job_category columns to job.

Revision ID: 4866ad7374ed
Revises: cdd9ea314360
Create Date: 2026-07-08 18:22:00.000000+08:00
\"\"\"
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '4866ad7374ed'
down_revision: Union[str, None] = 'cdd9ea314360'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('job', sa.Column('major', sa.String(200), nullable=True))
    op.add_column('job', sa.Column('job_category', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('job', 'job_category')
    op.drop_column('job', 'major')
'''

fp = r'C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\alembic\versions\2026_07_08_1822-4866ad7374ed_add_major_and_job_category.py'
with open(fp, 'w', encoding='utf-8') as f:
    f.write(mig_content)
print('Written OK')