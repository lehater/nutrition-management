from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal

from nutrition_management.food_knowledge.application.contracts import FoodFact, NutrientEvidenceStatus, NutrientFact
from nutrition_management.food_knowledge.application.imports import import_food
from nutrition_management.food_knowledge.infrastructure.repository import FoodKnowledgeRepository
from nutrition_management.market_catalog.application.imports import import_offer
from nutrition_management.market_catalog.domain.model import Availability, Offer
from nutrition_management.market_catalog.infrastructure.repository import MarketCatalogRepository
from nutrition_management.nutrition_targeting.application.imports import import_profile, import_standard
from nutrition_management.nutrition_targeting.domain.model import NutritionProfile, Sex
from nutrition_management.nutrition_targeting.infrastructure.repository import NutritionTargetingRepository

from fixture_loader import HOUSEHOLD_ID, MARKET_AS_OF, load_acceptance_fixture, test_standard


def test_file_database_uses_required_sqlite_pragmas(engine):
    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA journal_mode").scalar_one().lower() == "wal"
        assert connection.exec_driver_sql("PRAGMA synchronous").scalar_one() == 2
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
        assert connection.exec_driver_sql("PRAGMA read_uncommitted").scalar_one() == 0


def test_decimal_nutrient_value_round_trips_without_binary_float(engine):
    with engine.begin() as connection:
        repo = FoodKnowledgeRepository(connection)
        import_food(
            repo,
            FoodFact(
                base_food_id="precision-food",
                name="Precision Food",
                category="grains_cereal_products_potatoes",
                source_name="test",
                source_version="1",
                nutrients=(NutrientFact("FIBT", NutrientEvidenceStatus.KNOWN, Decimal("1.234567890123456789")),),
            ),
        )
    with engine.connect() as connection:
        value = FoodKnowledgeRepository(connection).get_food("precision-food").nutrient("FIBT").amount_per_100g
    assert value == Decimal("1.234567890123456789")


def test_standard_versions_can_reuse_reference_ids_and_only_one_is_active(engine):
    first = test_standard()
    second = replace(first, version="test-slice-v2")

    with engine.begin() as connection:
        repo = NutritionTargetingRepository(connection)
        import_standard(repo, first, active=True)
        import_standard(repo, second, active=True)

    with engine.connect() as connection:
        active = NutritionTargetingRepository(connection).active_standard()
    assert active.version == "test-slice-v2"
    assert {item.reference_id for item in active.references} == {item.reference_id for item in first.references}


def test_pal_adjustment_provenance_round_trips(engine):
    profile = NutritionProfile(
        member_id="adjusted",
        date_of_birth=date(1990, 1, 1),
        sex=Sex.FEMALE,
        height_m=Decimal("1.70"),
        current_weight_kg=Decimal("70"),
        current_weight_date=date(2026, 9, 14),
        pal=Decimal("2.5"),
        pal_activity_adjustment_applied=True,
    )
    with engine.begin() as connection:
        import_profile(NutritionTargetingRepository(connection), "h-adjusted", profile)
    with engine.connect() as connection:
        loaded = NutritionTargetingRepository(connection).profiles_for_household("h-adjusted")[0]
    assert loaded.pal == Decimal("2.5")
    assert loaded.pal_activity_adjustment_applied is True


def test_one_read_transaction_keeps_coherent_snapshot_across_later_writer_commit(engine):
    load_acceptance_fixture(engine)

    reader = engine.connect()
    transaction = reader.begin()
    try:
        # First read establishes SQLite's WAL snapshot.
        NutritionTargetingRepository(reader).profiles_for_household(HOUSEHOLD_ID)

        with engine.begin() as writer:
            import_offer(
                MarketCatalogRepository(writer),
                Offer(
                    offer_id="offer-committed-later",
                    sku_id="sku-01",
                    channel_id="merchant-a-pickup",
                    price=Decimal("0.99"),
                    currency="EUR",
                    availability=Availability.AVAILABLE,
                    observed_at=MARKET_AS_OF + timedelta(minutes=1),
                ),
            )

        old_snapshot_ids = {item.offer_id for item in MarketCatalogRepository(reader).offers()}
        assert "offer-committed-later" not in old_snapshot_ids
    finally:
        transaction.rollback()
        reader.close()

    with engine.connect() as fresh_reader:
        fresh_ids = {item.offer_id for item in MarketCatalogRepository(fresh_reader).offers()}
    assert "offer-committed-later" in fresh_ids
