"""Add explicit safety mapping registry.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "nt_safety_mapping",
        sa.Column("standard_version", sa.String(), sa.ForeignKey("nt_standard_set.version"), primary_key=True),
        sa.Column("family_id", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("nutrient_measure", sa.String()),
        sa.Column("canonical_unit", sa.String()),
        sa.Column("reason", sa.String()),
    )


def downgrade() -> None:
    op.drop_table("nt_safety_mapping")
