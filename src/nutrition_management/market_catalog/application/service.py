from __future__ import annotations

from datetime import datetime

from nutrition_management.food_knowledge.application.contracts import (
    FoodFact,
    NutrientEvidenceStatus,
    NutrientFact,
)
from nutrition_management.market_catalog.application.contracts import ExecutableOfferFact
from nutrition_management.market_catalog.domain.model import FulfilmentChannel, Offer, ProductCard


def _effective_nutrients(food: FoodFact, product: ProductCard) -> tuple[NutrientFact, ...]:
    values = {item.measure: item for item in food.nutrients}
    for override in product.nutrient_overrides:
        values[override.measure] = NutrientFact(
            measure=override.measure,
            status=NutrientEvidenceStatus.ZERO if override.amount_per_100g == 0 else NutrientEvidenceStatus.KNOWN,
            amount_per_100g=override.amount_per_100g,
        )
    return tuple(values[key] for key in sorted(values))


def executable_market_projection(
    *,
    products: tuple[ProductCard, ...],
    channels: tuple[FulfilmentChannel, ...],
    offers: tuple[Offer, ...],
    food_lookup,
    as_of: datetime,
) -> tuple[ExecutableOfferFact, ...]:
    products_by_id = {item.sku_id: item for item in products}
    channels_by_id = {item.channel_id: item for item in channels}
    result: list[ExecutableOfferFact] = []

    for offer in offers:
        product = products_by_id[offer.sku_id]
        channel = channels_by_id[offer.channel_id]
        if not offer.is_executable_at(as_of) or not channel.is_valid_at(as_of):
            continue
        if offer.currency != channel.currency:
            continue
        if product.edible_grams_per_package <= 0:
            continue
        food = food_lookup(product.base_food_id)
        result.append(
            ExecutableOfferFact(
                offer_id=offer.offer_id,
                sku_id=product.sku_id,
                base_food_id=product.base_food_id,
                food_name=food.name,
                category=food.category,
                merchant_id=channel.merchant_id,
                channel_id=channel.channel_id,
                fulfilment_mode=channel.mode.value,
                edible_grams_per_package=product.edible_grams_per_package,
                package_price=offer.price,
                currency=offer.currency,
                minimum_order=channel.minimum_order,
                fulfilment_fee=channel.fulfilment_fee,
                free_delivery_threshold=channel.free_delivery_threshold,
                nutrients=_effective_nutrients(food, product),
                observed_at=offer.observed_at,
                valid_from=offer.valid_from,
                valid_until=offer.valid_until,
            )
        )

    return tuple(sorted(result, key=lambda item: item.offer_id))
