"""Add production Nutrition Standard Set semantics.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("nt_standard_set") as batch:
        batch.add_column(sa.Column("content_digest", sa.String()))
        batch.add_column(sa.Column("source_manifest", sa.String()))

    with op.batch_alter_table("nt_standard_reference") as batch:
        batch.add_column(sa.Column("family_id", sa.String()))
        batch.add_column(sa.Column("source_semantic_kind", sa.String()))
        batch.add_column(sa.Column("source_unit", sa.String()))
        batch.add_column(sa.Column("scope", sa.String()))
        batch.add_column(sa.Column("applicability_json", sa.String()))
        batch.add_column(sa.Column("applicable_weight_rule", sa.String()))
        batch.add_column(sa.Column("source_id", sa.String()))
        batch.add_column(sa.Column("source_locator", sa.String()))

    op.create_table(
        "nt_reference_mapping",
        sa.Column("standard_version", sa.String(), sa.ForeignKey("nt_standard_set.version"), primary_key=True),
        sa.Column("family_id", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("nutrient_measure", sa.String()),
        sa.Column("canonical_unit", sa.String()),
        sa.Column("formula_id", sa.String()),
        sa.Column("reason", sa.String()),
    )

    with op.batch_alter_table("nt_safety_reference") as batch:
        batch.add_column(sa.Column("family_id", sa.String()))
        batch.add_column(sa.Column("semantic_kind", sa.String()))
        batch.add_column(sa.Column("source_unit", sa.String()))
        batch.add_column(sa.Column("scope", sa.String()))
        batch.add_column(sa.Column("applicability_json", sa.String()))
        batch.add_column(sa.Column("substance_scope", sa.String()))
        batch.add_column(sa.Column("source_id", sa.String()))
        batch.add_column(sa.Column("source_locator", sa.String()))


def downgrade() -> None:
    with op.batch_alter_table("nt_safety_reference") as batch:
        batch.drop_column("source_locator")
        batch.drop_column("source_id")
        batch.drop_column("substance_scope")
        batch.drop_column("applicability_json")
        batch.drop_column("scope")
        batch.drop_column("source_unit")
        batch.drop_column("semantic_kind")
        batch.drop_column("family_id")

    op.drop_table("nt_reference_mapping")

    with op.batch_alter_table("nt_standard_reference") as batch:
        batch.drop_column("source_locator")
        batch.drop_column("source_id")
        batch.drop_column("applicable_weight_rule")
        batch.drop_column("applicability_json")
        batch.drop_column("scope")
        batch.drop_column("source_unit")
        batch.drop_column("source_semantic_kind")
        batch.drop_column("family_id")

    with op.batch_alter_table("nt_standard_set") as batch:
        batch.drop_column("source_manifest")
        batch.drop_column("content_digest")
