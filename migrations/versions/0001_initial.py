"""Initial context-owned provider schema.

Revision ID: 0001
Revises:
Create Date: 2026-09-15
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nutrition Targeting ownership.
    op.create_table(
        "nt_member_profile",
        sa.Column("member_id", sa.String(), primary_key=True),
        sa.Column("household_id", sa.String(), nullable=False),
        sa.Column("date_of_birth", sa.String(), nullable=False),
        sa.Column("sex", sa.String(), nullable=False),
        sa.Column("height_m", sa.String(), nullable=False),
        sa.Column("current_weight_kg", sa.String(), nullable=False),
        sa.Column("current_weight_date", sa.String(), nullable=False),
        sa.Column("pal", sa.String(), nullable=False),
        sa.Column("target_weight_kg", sa.String()),
        sa.Column("target_date", sa.String()),
    )
    op.create_index("ix_nt_member_profile_household_id", "nt_member_profile", ["household_id"])
    op.create_table(
        "nt_standard_set",
        sa.Column("version", sa.String(), primary_key=True),
        sa.Column("active", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "nt_standard_reference",
        sa.Column("reference_id", sa.String(), primary_key=True),
        sa.Column("standard_version", sa.String(), sa.ForeignKey("nt_standard_set.version"), nullable=False),
        sa.Column("nutrient_measure", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("basis", sa.String(), nullable=False),
        sa.Column("lower_value", sa.String()),
        sa.Column("upper_value", sa.String()),
        sa.Column("point_value", sa.String()),
        sa.Column("energy_kcal_per_g", sa.String()),
    )
    op.create_table(
        "nt_safety_reference",
        sa.Column("reference_id", sa.String(), primary_key=True),
        sa.Column("standard_version", sa.String(), sa.ForeignKey("nt_standard_set.version"), nullable=False),
        sa.Column("nutrient_measure", sa.String(), nullable=False),
        sa.Column("daily_upper", sa.String(), nullable=False),
    )

    # Food Knowledge ownership.
    op.create_table(
        "fk_base_food",
        sa.Column("base_food_id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("source_version", sa.String()),
    )
    op.create_table(
        "fk_nutrient_value",
        sa.Column("base_food_id", sa.String(), sa.ForeignKey("fk_base_food.base_food_id"), primary_key=True),
        sa.Column("measure", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("amount_per_100g", sa.String()),
    )

    # Market Catalog ownership. Cross-context IDs are scalar only: no FK to fk_* tables.
    op.create_table(
        "mc_product_card",
        sa.Column("sku_id", sa.String(), primary_key=True),
        sa.Column("base_food_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("edible_grams_per_package", sa.String(), nullable=False),
    )
    op.create_table(
        "mc_product_nutrient_override",
        sa.Column("sku_id", sa.String(), sa.ForeignKey("mc_product_card.sku_id"), primary_key=True),
        sa.Column("measure", sa.String(), primary_key=True),
        sa.Column("amount_per_100g", sa.String(), nullable=False),
    )
    op.create_table(
        "mc_fulfilment_channel",
        sa.Column("channel_id", sa.String(), primary_key=True),
        sa.Column("merchant_id", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("minimum_order", sa.String(), nullable=False),
        sa.Column("fulfilment_fee", sa.String(), nullable=False),
        sa.Column("free_delivery_threshold", sa.String()),
        sa.Column("observed_at", sa.String()),
        sa.Column("valid_from", sa.String()),
        sa.Column("valid_until", sa.String()),
    )
    op.create_table(
        "mc_offer",
        sa.Column("offer_id", sa.String(), primary_key=True),
        sa.Column("sku_id", sa.String(), sa.ForeignKey("mc_product_card.sku_id"), nullable=False),
        sa.Column("channel_id", sa.String(), sa.ForeignKey("mc_fulfilment_channel.channel_id"), nullable=False),
        sa.Column("price", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("availability", sa.String(), nullable=False),
        sa.Column("observed_at", sa.String(), nullable=False),
        sa.Column("valid_from", sa.String()),
        sa.Column("valid_until", sa.String()),
    )


def downgrade() -> None:
    op.drop_table("mc_offer")
    op.drop_table("mc_fulfilment_channel")
    op.drop_table("mc_product_nutrient_override")
    op.drop_table("mc_product_card")
    op.drop_table("fk_nutrient_value")
    op.drop_table("fk_base_food")
    op.drop_table("nt_safety_reference")
    op.drop_table("nt_standard_reference")
    op.drop_table("nt_standard_set")
    op.drop_index("ix_nt_member_profile_household_id", table_name="nt_member_profile")
    op.drop_table("nt_member_profile")
