"""Persist source reference bound inclusivity.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("nt_standard_reference") as batch:
        batch.add_column(sa.Column("lower_inclusive", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch.add_column(sa.Column("upper_inclusive", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    with op.batch_alter_table("nt_standard_reference") as batch:
        batch.drop_column("upper_inclusive")
        batch.drop_column("lower_inclusive")
