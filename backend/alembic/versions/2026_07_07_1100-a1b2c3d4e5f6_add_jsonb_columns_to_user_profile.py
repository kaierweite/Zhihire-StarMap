"""add JSONB columns to user_profile

Revision ID: a1b2c3d4e5f6
Revises: dde25d9d8bd4
Create Date: 2026-07-07 11:00:00.000000+08:00

为 user_profile 表添加 4 个多值 JSONB 列：
work_experiences、project_experiences、languages、certificates，
支撑前端档案编辑中工作/项目/语言/证书四个 section 的数据持久化。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "dde25d9d8bd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 工作/实习经历 JSONB 数组
    op.add_column("user_profile", sa.Column("work_experiences", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))
    # 项目经历 JSONB 数组
    op.add_column("user_profile", sa.Column("project_experiences", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))
    # 语言能力 JSONB 数组
    op.add_column("user_profile", sa.Column("languages", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))
    # 证书 JSONB 数组
    op.add_column("user_profile", sa.Column("certificates", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))


def downgrade() -> None:
    op.drop_column("user_profile", "certificates")
    op.drop_column("user_profile", "languages")
    op.drop_column("user_profile", "project_experiences")
    op.drop_column("user_profile", "work_experiences")
