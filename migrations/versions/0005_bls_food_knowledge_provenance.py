"""Add source-rich Food Knowledge persistence for BLS imports.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fk_source_dataset",
        sa.Column("source_id", sa.String(), primary_key=True),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("source_version", sa.String(), nullable=False),
        sa.Column("source_digest", sa.String(), nullable=False),
        sa.Column("package_digest", sa.String(), nullable=False),
        sa.Column("doi", sa.String(), nullable=False),
        sa.Column("license", sa.String(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=False),
        sa.Column("attribution", sa.String(), nullable=False),
        sa.Column("manifest_json", sa.String(), nullable=False),
    )
    op.create_table(
        "fk_component",
        sa.Column(
            "source_id",
            sa.String(),
            sa.ForeignKey("fk_source_dataset.source_id"),
            primary_key=True,
        ),
        sa.Column("component_code", sa.String(), primary_key=True),
        sa.Column("name_de", sa.String(), nullable=False),
        sa.Column("name_en", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("group_de", sa.String()),
        sa.Column("group_en", sa.String()),
        sa.Column("formula", sa.String()),
        sa.Column("formula_application", sa.String()),
    )

    op.add_column("fk_base_food", sa.Column("source_id", sa.String()))
    op.add_column("fk_base_food", sa.Column("source_code", sa.String()))
    op.add_column("fk_base_food", sa.Column("name_en", sa.String()))
    op.create_index(
        "uq_fk_base_food_source_code",
        "fk_base_food",
        ["source_id", "source_code"],
        unique=True,
    )

    op.add_column("fk_nutrient_value", sa.Column("source_value_text", sa.String()))
    op.add_column("fk_nutrient_value", sa.Column("value_origin", sa.String()))
    op.add_column("fk_nutrient_value", sa.Column("source_reference", sa.String()))


def downgrade() -> None:
    op.drop_column("fk_nutrient_value", "source_reference")
    op.drop_column("fk_nutrient_value", "value_origin")
    op.drop_column("fk_nutrient_value", "source_value_text")

    op.drop_index("uq_fk_base_food_source_code", table_name="fk_base_food")
    op.drop_column("fk_base_food", "name_en")
    op.drop_column("fk_base_food", "source_code")
    op.drop_column("fk_base_food", "source_id")

    op.drop_table("fk_component")
    op.drop_table("fk_source_dataset")
