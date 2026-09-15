from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from nutrition_management.food_knowledge.application.contracts import FoodFact, NutrientEvidenceStatus, NutrientFact
from nutrition_management.market_catalog.application.service import executable_market_projection
from nutrition_management.market_catalog.domain.model import (
    Availability,
    FulfilmentChannel,
    FulfilmentMode,
    NormalizedNutrientOverride,
    Offer,
    ProductCard,
)

NOW = datetime(2026, 9, 15, 12, tzinfo=UTC)


def food_lookup(_food_id: str) -> FoodFact:
    return FoodFact(
        base_food_id="food-1",
        name="Base Food",
        category="fruit_and_vegetables",
        source_name="test",
        source_version="1",
        nutrients=(
            NutrientFact("ENERCC", NutrientEvidenceStatus.KNOWN, Decimal("100")),
            NutrientFact("FIBT", NutrientEvidenceStatus.TRACE, None),
        ),
    )


def test_product_override_replaces_only_matching_normalized_component():
    product = ProductCard(
        sku_id="sku-1",
        base_food_id="food-1",
        name="SKU",
        edible_grams_per_package=Decimal("500"),
        nutrient_overrides=(NormalizedNutrientOverride("ENERCC", Decimal("120")),),
    )
    channel = FulfilmentChannel("channel", "merchant", FulfilmentMode.PICKUP, "EUR", observed_at=NOW)
    offer = Offer("offer", "sku-1", "channel", Decimal("2.50"), "EUR", Availability.AVAILABLE, NOW)

    fact = executable_market_projection(
        products=(product,), channels=(channel,), offers=(offer,), food_lookup=food_lookup, as_of=NOW
    )[0]
    energy = next(item for item in fact.nutrients if item.measure == "ENERCC")
    fiber = next(item for item in fact.nutrients if item.measure == "FIBT")
    assert energy.amount_per_100g == Decimal("120")
    assert energy.status == NutrientEvidenceStatus.KNOWN
    assert fiber.status == NutrientEvidenceStatus.TRACE


def test_unavailable_expired_and_future_observations_do_not_enter_projection():
    product = ProductCard("sku-1", "food-1", "SKU", Decimal("500"))
    channel = FulfilmentChannel("channel", "merchant", FulfilmentMode.PICKUP, "EUR", observed_at=NOW)
    future_channel = FulfilmentChannel(
        "future-channel",
        "merchant",
        FulfilmentMode.PICKUP,
        "EUR",
        observed_at=NOW + timedelta(minutes=1),
    )
    offers = (
        Offer("ok", "sku-1", "channel", Decimal("2"), "EUR", Availability.AVAILABLE, NOW),
        Offer("unavailable", "sku-1", "channel", Decimal("1"), "EUR", Availability.UNAVAILABLE, NOW),
        Offer(
            "expired",
            "sku-1",
            "channel",
            Decimal("1"),
            "EUR",
            Availability.AVAILABLE,
            NOW - timedelta(days=2),
            valid_until=NOW - timedelta(days=1),
        ),
        Offer(
            "future-offer",
            "sku-1",
            "channel",
            Decimal("1"),
            "EUR",
            Availability.AVAILABLE,
            NOW + timedelta(minutes=1),
        ),
        Offer(
            "future-channel-offer",
            "sku-1",
            "future-channel",
            Decimal("1"),
            "EUR",
            Availability.AVAILABLE,
            NOW,
        ),
    )
    facts = executable_market_projection(
        products=(product,),
        channels=(channel, future_channel),
        offers=offers,
        food_lookup=food_lookup,
        as_of=NOW,
    )
    assert [item.offer_id for item in facts] == ["ok"]


def test_market_instants_must_be_timezone_aware_and_channel_observation_is_required():
    naive = datetime(2026, 9, 15, 12)
    with pytest.raises(ValueError, match="timezone-aware"):
        Offer("offer", "sku", "channel", Decimal("1"), "EUR", Availability.AVAILABLE, naive)
    with pytest.raises(ValueError, match="timezone-aware"):
        FulfilmentChannel("channel", "merchant", FulfilmentMode.PICKUP, "EUR", observed_at=naive)
    with pytest.raises(ValueError, match="timezone-aware"):
        FulfilmentChannel("channel", "merchant", FulfilmentMode.PICKUP, "EUR", observed_at=NOW, valid_from=naive)
    with pytest.raises(ValueError, match="observed_at is required"):
        FulfilmentChannel("channel", "merchant", FulfilmentMode.PICKUP, "EUR")


def test_negative_commercial_values_and_nonpositive_edible_quantity_are_rejected():
    with pytest.raises(ValueError, match="edible package quantity"):
        ProductCard("sku", "food", "SKU", Decimal("0"))
    with pytest.raises(ValueError, match="offer price"):
        Offer("offer", "sku", "channel", Decimal("-0.01"), "EUR", Availability.AVAILABLE, NOW)
    with pytest.raises(ValueError, match="minimum order"):
        FulfilmentChannel(
            "channel",
            "merchant",
            FulfilmentMode.PICKUP,
            "EUR",
            minimum_order=Decimal("-1"),
            observed_at=NOW,
        )
