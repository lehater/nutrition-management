from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from nutrition_management.food_knowledge.application.contracts import (
    FoodFact,
    NutrientEvidenceStatus,
    NutrientFact,
)
from nutrition_management.food_knowledge.application.imports import import_food
from nutrition_management.food_knowledge.infrastructure.repository import FoodKnowledgeRepository
from nutrition_management.market_catalog.application.imports import import_channel, import_offer, import_product
from nutrition_management.market_catalog.domain.model import (
    Availability,
    FulfilmentChannel,
    FulfilmentMode,
    Offer,
    ProductCard,
)
from nutrition_management.market_catalog.infrastructure.repository import MarketCatalogRepository
from nutrition_management.nutrition_targeting.application.imports import import_profile, import_standard
from nutrition_management.nutrition_targeting.domain.model import (
    NutritionProfile,
    NutritionStandardSet,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceKind,
    SafetyDefinition,
    Sex,
)
from nutrition_management.nutrition_targeting.infrastructure.repository import NutritionTargetingRepository

DERIVATION_DATE = date(2026, 9, 15)
MARKET_AS_OF = datetime(2026, 9, 15, 12, 0, tzinfo=UTC)
HOUSEHOLD_ID = "household-1"


def test_standard() -> NutritionStandardSet:
    return NutritionStandardSet(
        version="test-slice-v1",
        references=(
            ReferenceDefinition(
                "protein",
                "PROT625",
                ReferenceKind.ADEQUACY_FLOOR,
                ReferenceBasis.PER_KG_DAILY,
                lower=Decimal("0.8"),
            ),
            ReferenceDefinition(
                "fiber",
                "FIBT",
                ReferenceKind.ADEQUACY_FLOOR,
                ReferenceBasis.ABSOLUTE_DAILY,
                lower=Decimal("30"),
            ),
            ReferenceDefinition(
                "carbohydrate-share",
                "CHO",
                ReferenceKind.INTERVAL,
                ReferenceBasis.PERCENT_ENERGY,
                lower=Decimal("0.45"),
                upper=Decimal("0.55"),
                energy_kcal_per_g=Decimal("4"),
            ),
            ReferenceDefinition(
                "salt-upper",
                "NACL",
                ReferenceKind.UPPER_BOUND,
                ReferenceBasis.ABSOLUTE_DAILY,
                upper=Decimal("6"),
            ),
        ),
        safety_limits=(SafetyDefinition("sodium-safety", "NA", Decimal("2.3")),),
    )


def _nutrients(index: int) -> tuple[NutrientFact, ...]:
    return (
        NutrientFact("ENERCC", NutrientEvidenceStatus.KNOWN, Decimal("200")),
        NutrientFact("PROT625", NutrientEvidenceStatus.KNOWN, Decimal("10") + Decimal(index % 2)),
        NutrientFact("FIBT", NutrientEvidenceStatus.KNOWN, Decimal("3")),
        NutrientFact("CHO", NutrientEvidenceStatus.KNOWN, Decimal("25")),
        NutrientFact("NACL", NutrientEvidenceStatus.KNOWN, Decimal("0.2")),
        NutrientFact("NA", NutrientEvidenceStatus.KNOWN, Decimal("0.08")),
    )


def load_acceptance_fixture(engine) -> None:
    with engine.begin() as connection:
        nt = NutritionTargetingRepository(connection)
        fk = FoodKnowledgeRepository(connection)
        mc = MarketCatalogRepository(connection)

        import_standard(nt, test_standard(), active=True)
        import_profile(
            nt,
            HOUSEHOLD_ID,
            NutritionProfile(
                member_id="alice",
                date_of_birth=date(1990, 1, 10),
                sex=Sex.FEMALE,
                height_m=Decimal("1.68"),
                current_weight_kg=Decimal("70"),
                current_weight_date=date(2026, 9, 10),
                pal=Decimal("1.6"),
            ),
        )
        import_profile(
            nt,
            HOUSEHOLD_ID,
            NutritionProfile(
                member_id="bob",
                date_of_birth=date(1988, 5, 20),
                sex=Sex.MALE,
                height_m=Decimal("1.82"),
                current_weight_kg=Decimal("70"),
                current_weight_date=date(2026, 9, 11),
                pal=Decimal("1.6"),
            ),
        )

        categories = (
            "fruit_and_vegetables",
            "fruit_and_vegetables",
            "legumes_nuts_seeds",
            "legumes_nuts_seeds",
            "grains_cereal_products_potatoes",
            "grains_cereal_products_potatoes",
            "milk_and_dairy",
            "milk_and_dairy",
        )
        for index, category in enumerate(categories, start=1):
            food_id = f"food-{index:02d}"
            import_food(
                fk,
                FoodFact(
                    base_food_id=food_id,
                    name=f"Fixture Food {index}",
                    category=category,
                    nutrients=_nutrients(index),
                    source_name="test-fixture",
                    source_version="1",
                ),
            )
            import_product(
                mc,
                ProductCard(
                    sku_id=f"sku-{index:02d}",
                    base_food_id=food_id,
                    name=f"Fixture SKU {index}",
                    edible_grams_per_package=Decimal("1000"),
                ),
            )

        pickup = FulfilmentChannel(
            channel_id="merchant-a-pickup",
            merchant_id="merchant-a",
            mode=FulfilmentMode.PICKUP,
            currency="EUR",
            minimum_order=Decimal(0),
            fulfilment_fee=Decimal(0),
            observed_at=MARKET_AS_OF - timedelta(days=1),
        )
        delivery = FulfilmentChannel(
            channel_id="merchant-b-delivery",
            merchant_id="merchant-b",
            mode=FulfilmentMode.DELIVERY,
            currency="EUR",
            minimum_order=Decimal("20"),
            fulfilment_fee=Decimal("5"),
            free_delivery_threshold=Decimal("100"),
            observed_at=MARKET_AS_OF - timedelta(days=1),
        )
        import_channel(mc, pickup)
        import_channel(mc, delivery)

        for index in range(1, 9):
            import_offer(
                mc,
                Offer(
                    offer_id=f"offer-a-{index:02d}",
                    sku_id=f"sku-{index:02d}",
                    channel_id=pickup.channel_id,
                    price=Decimal("2.00") + Decimal(index) / Decimal(100),
                    currency="EUR",
                    availability=Availability.AVAILABLE,
                    observed_at=MARKET_AS_OF - timedelta(hours=2),
                ),
            )

        # One competing cheaper offer. Its saving is small enough that the 5% cost-close
        # rule can still prefer the single pickup group when nutrition/variety are tied.
        import_offer(
            mc,
            Offer(
                offer_id="offer-b-01",
                sku_id="sku-01",
                channel_id=delivery.channel_id,
                price=Decimal("1.80"),
                currency="EUR",
                availability=Availability.AVAILABLE,
                observed_at=MARKET_AS_OF - timedelta(hours=1),
            ),
        )
        import_offer(
            mc,
            Offer(
                offer_id="offer-unavailable",
                sku_id="sku-02",
                channel_id=delivery.channel_id,
                price=Decimal("1.00"),
                currency="EUR",
                availability=Availability.UNAVAILABLE,
                observed_at=MARKET_AS_OF - timedelta(hours=1),
            ),
        )
        import_offer(
            mc,
            Offer(
                offer_id="offer-expired",
                sku_id="sku-03",
                channel_id=delivery.channel_id,
                price=Decimal("1.00"),
                currency="EUR",
                availability=Availability.AVAILABLE,
                observed_at=MARKET_AS_OF - timedelta(days=2),
                valid_until=MARKET_AS_OF - timedelta(days=1),
            ),
        )
