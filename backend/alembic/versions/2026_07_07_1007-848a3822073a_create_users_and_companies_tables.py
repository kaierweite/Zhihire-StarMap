"""create users and companies tables

Revision ID: 848a3822073a
Revises: dde25d9d8bd4
Create Date: 2026-07-07 10:07:36.002303+08:00

仅创建 day01 认证模块所需的 `users` 与 `companies` 两张表。
数据库中已存在的早期 SQL 脚本表（单数名 `user`/`company` 等）保持不动，
避免破坏尚未由 ORM 接管的领域表；后续各 day 在引入对应实体时再分别迁移。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "848a3822073a"
down_revision: Union[str, None] = "dde25d9d8bd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 用户主表：bcrypt 密码哈希、语义化角色/状态、软删除时间戳
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # 用户名唯一索引
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # 企业档案表：关联用户主键、审核状态默认未审核
    op.create_table(
        "companies",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("company_name", sa.String(length=128), nullable=False),
        sa.Column("audit_status", sa.String(length=16), nullable=False),
        sa.Column("contact_email", sa.String(length=128), nullable=True),
        sa.Column("contact_phone", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # 企业关联用户唯一索引
    op.create_index(op.f("ix_companies_user_id"), "companies", ["user_id"], unique=True)


def downgrade() -> None:
    # 回滚：仅撤销 day01 新建的两张表与索引
    op.drop_index(op.f("ix_companies_user_id"), table_name="companies")
    op.drop_table("companies")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
