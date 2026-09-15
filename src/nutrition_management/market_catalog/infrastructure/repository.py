from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, MetaData, String, Table, select

from nutrition_management.market_catalog.domain.model import (
    Availability,
    FulfilmentChannel,
    FulfilmentMode,
    NormalizedNutrientOverride,
    Offer,
    ProductCard,
)

metadata = MetaData()

product_table = Table(
    "mc_product_card",
    metadata,
    Column("sku_id", String, primary_key=True),
    Column("base_food_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("edible_grams_per_package", String, nullable=False),
)

override_table = Table(
    "mc_product_nutrient_override",
    metadata,
    Column("sku_id", String, ForeignKey("mc_product_card.sku_id"), primary_key=True),
    Column("measure", String, primary_key=True),
    Column("amount_per_100g", String, nullable=False),
)

channel_table = Table(
    "mc_fulfilment_channel",
    metadata,
    Column("channel_id", String, primary_key=True),
    Column("merchant_id", String, nullable=False),
    Column("mode", String, nullable=False),
    Column("currency", String, nullable=False),
    Column("minimum_order", String, nullable=False),
    Column("fulfilment_fee", String, nullable=False),
    Column("free_delivery_threshold", String),
    Column("observed_at", String),
    Column("valid_from", String),
    Column("valid_until", String),
)

offer_table = Table(
    "mc_offer",
    metadata,
    Column("offer_id", String, primary_key=True),
    Column("sku_id", String, ForeignKey("mc_product_card.sku_id"), nullable=False),
    Column("channel_id", String, ForeignKey("mc_fulfilment_channel.channel_id"), nullable=False),
    Column("price", String, nullable=False),
    Column("currency", String, nullable=False),
    Column("availability", String, nullable=False),
    Column("observed_at", String, nullable=False),
    Column("valid_from", String),
    Column("valid_until", String),
)


def _dt(value: str | None):
    return None if value is None else datetime.fromisoformat(value)


def _dec(value: str | None):
    return None if value is None else Decimal(value)


class MarketCatalogRepository:
    def __init__(self, connection):
        self._connection = connection

    def add_product(self, product: ProductCard) -> None:
        self._connection.execute(
            product_table.insert().values(
                sku_id=product.sku_id,
                base_food_id=product.base_food_id,
                name=product.name,
                edible_grams_per_package=str(product.edible_grams_per_package),
            )
        )
        for item in product.nutrient_overrides:
            self._connection.execute(
                override_table.insert().values(
                    sku_id=product.sku_id,
                    measure=item.measure,
                    amount_per_100g=str(item.amount_per_100g),
                )
            )

    def add_channel(self, channel: FulfilmentChannel) -> None:
        self._connection.execute(
            channel_table.insert().values(
                channel_id=channel.channel_id,
                merchant_id=channel.merchant_id,
                mode=channel.mode.value,
                currency=channel.currency,
                minimum_order=str(channel.minimum_order),
                fulfilment_fee=str(channel.fulfilment_fee),
                free_delivery_threshold=None if channel.free_delivery_threshold is None else str(channel.free_delivery_threshold),
                observed_at=None if channel.observed_at is None else channel.observed_at.isoformat(),
                valid_from=None if channel.valid_from is None else channel.valid_from.isoformat(),
                valid_until=None if channel.valid_until is None else channel.valid_until.isoformat(),
            )
        )

    def add_offer(self, offer: Offer) -> None:
        self._connection.execute(
            offer_table.insert().values(
                offer_id=offer.offer_id,
                sku_id=offer.sku_id,
                channel_id=offer.channel_id,
                price=str(offer.price),
                currency=offer.currency,
                availability=offer.availability.value,
                observed_at=offer.observed_at.isoformat(),
                valid_from=None if offer.valid_from is None else offer.valid_from.isoformat(),
                valid_until=None if offer.valid_until is None else offer.valid_until.isoformat(),
            )
        )

    def products(self) -> tuple[ProductCard, ...]:
        rows = self._connection.execute(select(product_table).order_by(product_table.c.sku_id)).mappings()
        result = []
        for row in rows:
            overrides = self._connection.execute(
                select(override_table).where(override_table.c.sku_id == row["sku_id"]).order_by(override_table.c.measure)
            ).mappings()
            result.append(
                ProductCard(
                    sku_id=row["sku_id"],
                    base_food_id=row["base_food_id"],
                    name=row["name"],
                    edible_grams_per_package=Decimal(row["edible_grams_per_package"]),
                    nutrient_overrides=tuple(
                        NormalizedNutrientOverride(item["measure"], Decimal(item["amount_per_100g"]))
                        for item in overrides
                    ),
                )
            )
        return tuple(result)

    def channels(self) -> tuple[FulfilmentChannel, ...]:
        rows = self._connection.execute(select(channel_table).order_by(channel_table.c.channel_id)).mappings()
        return tuple(
            FulfilmentChannel(
                channel_id=row["channel_id"],
                merchant_id=row["merchant_id"],
                mode=FulfilmentMode(row["mode"]),
                currency=row["currency"],
                minimum_order=Decimal(row["minimum_order"]),
                fulfilment_fee=Decimal(row["fulfilment_fee"]),
                free_delivery_threshold=_dec(row["free_delivery_threshold"]),
                observed_at=_dt(row["observed_at"]),
                valid_from=_dt(row["valid_from"]),
                valid_until=_dt(row["valid_until"]),
            )
            for row in rows
        )

    def offers(self) -> tuple[Offer, ...]:
        rows = self._connection.execute(select(offer_table).order_by(offer_table.c.offer_id)).mappings()
        return tuple(
            Offer(
                offer_id=row["offer_id"],
                sku_id=row["sku_id"],
                channel_id=row["channel_id"],
                price=Decimal(row["price"]),
                currency=row["currency"],
                availability=Availability(row["availability"]),
                observed_at=datetime.fromisoformat(row["observed_at"]),
                valid_from=_dt(row["valid_from"]),
                valid_until=_dt(row["valid_until"]),
            )
            for row in rows
        )
