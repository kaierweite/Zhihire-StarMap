"""day04_create_graph_related_tables

Create 4 new tables for the ability graph module:
- skill_relation: skill-to-skill semantic relationships
- role: career role definitions
- role_skill: role-to-skill requirement mapping
- ability_graph: graph JSON cache by owner

Revision ID: 0ec0a06ad127
Revises: 0bf683c512b7
Create Date: 2026-07-07 16:00:00.000000+08:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0ec0a06ad127"
down_revision: Union[str, None] = "0bf683c512b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ===== 1. role — 职业角色 =====
    op.create_table(
        "role",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'NORMAL'")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_role_name"), "role", ["name"], unique=True)

    # ===== 2. role_skill — 角色-技能关联 =====
    op.create_table(
        "role_skill",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("role_id", sa.BigInteger(), sa.ForeignKey("role.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("skill_id", sa.BigInteger(), sa.ForeignKey("skill.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("requirement_level", sa.String(10), nullable=False, server_default=sa.text("'MUST'")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )

    # ===== 3. skill_relation — 技能关系 =====
    op.create_table(
        "skill_relation",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("skill_id_a", sa.BigInteger(), sa.ForeignKey("skill.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("skill_id_b", sa.BigInteger(), sa.ForeignKey("skill.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("relation_type", sa.String(20), nullable=False, server_default=sa.text("'SIMILAR'")),
        sa.Column("weight", sa.Float(), nullable=False, server_default=sa.text("0.5")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )

    # ===== 4. ability_graph — 图谱缓存 =====
    op.create_table(
        "ability_graph",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("owner_type", sa.String(10), nullable=False, index=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("graph_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.String(1), nullable=False, server_default=sa.text("'0'::character varying")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ability_graph")
    op.drop_table("skill_relation")
    op.drop_table("role_skill")
    op.drop_index(op.f("ix_role_name"), table_name="role")
    op.drop_table("role")
