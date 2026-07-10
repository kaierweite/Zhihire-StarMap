"""create relational sub-tables for profile multi-value fields

Revision ID: c6d5e4f3a2b1
Revises: a1b2c3d4e5f6
Create Date: 2026-07-07 11:30:00.000000+08:00

替换 user_profile 上的 4 个 JSONB 列为正式子表：
  user_work_experience  工作/实习经历
  user_project_experience 项目经历
  user_language         语言能力
  user_certificate      证书

同时为 user_profile 补充求职意向字段：
  expected_position   期望职位
  expected_worktype   工作类型（全职/兼职/实习）
  expected_industry   期望行业
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "c6d5e4f3a2b1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ===== 1. 删除 JSONB 列 =====
    op.drop_column("user_profile", "certificates")
    op.drop_column("user_profile", "languages")
    op.drop_column("user_profile", "project_experiences")
    op.drop_column("user_profile", "work_experiences")

    # ===== 2. 建 4 张子表（字段对齐前端结构） =====
    op.create_table(
        "user_work_experience",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("company", sa.String(200), nullable=False),
        sa.Column("period", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_work_experience_user_id"), "user_work_experience", ["user_id"])

    op.create_table(
        "user_project_experience",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_project_experience_user_id"), "user_project_experience", ["user_id"])

    op.create_table(
        "user_language",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("language", sa.String(50), nullable=False),
        sa.Column("level", sa.String(20), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_language_user_id"), "user_language", ["user_id"])

    op.create_table(
        "user_certificate",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_certificate_user_id"), "user_certificate", ["user_id"])

    # ===== 3. user_profile 补充求职意向列 =====
    op.add_column("user_profile", sa.Column("expected_position", sa.String(200), nullable=True))
    op.add_column("user_profile", sa.Column("expected_worktype", sa.String(20), nullable=True))
    op.add_column("user_profile", sa.Column("expected_industry", sa.String(100), nullable=True))


def downgrade() -> None:
    # 意向列
    op.drop_column("user_profile", "expected_industry")
    op.drop_column("user_profile", "expected_worktype")
    op.drop_column("user_profile", "expected_position")

    # 子表
    op.drop_index(op.f("ix_user_certificate_user_id"), table_name="user_certificate")
    op.drop_table("user_certificate")
    op.drop_index(op.f("ix_user_language_user_id"), table_name="user_language")
    op.drop_table("user_language")
    op.drop_index(op.f("ix_user_project_experience_user_id"), table_name="user_project_experience")
    op.drop_table("user_project_experience")
    op.drop_index(op.f("ix_user_work_experience_user_id"), table_name="user_work_experience")
    op.drop_table("user_work_experience")

    # 恢复 JSONB 列
    op.add_column("user_profile", sa.Column("certificates", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))
    op.add_column("user_profile", sa.Column("languages", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))
    op.add_column("user_profile", sa.Column("project_experiences", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))
    op.add_column("user_profile", sa.Column("work_experiences", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")))
