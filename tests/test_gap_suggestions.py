from datetime import UTC, date, datetime
from decimal import Decimal

from nutrition_management.food_knowledge.application.contracts import (
    FoodFact,
    NutrientEvidenceStatus,
    NutrientFact,
)
from nutrition_management.food_knowledge.application.queries import (
    theoretical_foods_with_positive_measure,
)
from nutrition_management.purchase_planning.application.service import (
    generate_purchase_plan,
)
from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    PlanningInputSnapshot,
    PurchaseCandidate,
    SolverDecision,
    SolverLineDecision,
    TargetDimension,
    TargetKind,
    TheoreticalFoodCandidate,
)
from nutrition_management.purchase_planning.domain.suggestions import (
    positive_gap_measures,
    rank_gap_suggestions,
)

NOW = datetime(2026, 9, 19, 10, tzinfo=UTC)
TODAY = date(2026, 9, 19)


class FoodRepository:
    def __init__(self, foods):
        self._foods = tuple(foods)

    def all_foods(self):
        return self._foods


class SnapshotSource:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def capture(self, household_id, derivation_date, market_as_of):
        return self.snapshot


class SuggestionSource:
    def __init__(self, by_measure):
        self.by_measure = by_measure
        self.calls = []

    def candidates_for_measure(self, measure):
        self.calls.append(measure)
        return self.by_measure.get(measure, ())


def food(food_id, measure_status, measure_amount, *, energy_status=NutrientEvidenceStatus.KNOWN, energy_amount=Decimal("100")):
    return FoodFact(
        base_food_id=food_id,
        name=food_id,
        category="fruit_and_vegetables",
        nutrients=(
            NutrientFact("FIBT", measure_status, measure_amount),
            NutrientFact("ENERCC", energy_status, energy_amount),
        ),
        source_name="fixture",
        source_version="1",
    )


def test_food_knowledge_query_publishes_only_known_positive_measure():
    foods = (
        food("known", NutrientEvidenceStatus.KNOWN, Decimal("5")),
        food("zero", NutrientEvidenceStatus.ZERO, Decimal("0")),
        food("trace", NutrientEvidenceStatus.TRACE, None),
        food("missing", NutrientEvidenceStatus.MISSING, None),
    )

    result = theoretical_foods_with_positive_measure(FoodRepository(foods), "FIBT")

    assert tuple(item.base_food_id for item in result) == ("known",)


def test_non_energy_ranking_prefers_computable_per_100kcal_then_fallback():
    foods = (
        TheoreticalFoodCandidate(
            "fallback",
            "Fallback",
            "legumes_nuts_seeds",
            Decimal("100"),
            None,
            "fixture",
        ),
        TheoreticalFoodCandidate(
            "ratio-5",
            "Ratio 5",
            "fruit_and_vegetables",
            Decimal("5"),
            Decimal("100"),
            "fixture",
        ),
        TheoreticalFoodCandidate(
            "ratio-8",
            "Ratio 8",
            "milk_and_dairy",
            Decimal("4"),
            Decimal("50"),
            "fixture",
        ),
    )

    result = rank_gap_suggestions(
        measure="FIBT",
        foods=foods,
        represented_categories=(),
    )

    assert tuple(item.base_food_id for item in result) == (
        "ratio-8",
        "ratio-5",
        "fallback",
    )
    assert result[0].amount_per_100kcal == Decimal("8")
    assert result[-1].amount_per_100kcal is None


def test_energy_gap_ranks_directly_by_energy_per_100g():
    foods = (
        TheoreticalFoodCandidate(
            "lower",
            "Lower",
            "fruit_and_vegetables",
            Decimal("200"),
            Decimal("200"),
            "fixture",
        ),
        TheoreticalFoodCandidate(
            "higher",
            "Higher",
            "milk_and_dairy",
            Decimal("300"),
            Decimal("300"),
            "fixture",
        ),
    )

    result = rank_gap_suggestions(
        measure="ENERCC",
        foods=foods,
        represented_categories=(),
    )

    assert tuple(item.base_food_id for item in result) == ("higher", "lower")
    assert all(item.amount_per_100kcal is None for item in result)


def _snapshot(targets):
    candidate = PurchaseCandidate(
        offer_id="offer",
        sku_id="sku",
        base_food_id="market-food",
        food_name="Market Food",
        category="fruit_and_vegetables",
        merchant_id="merchant",
        channel_id="channel",
        fulfilment_mode="pickup",
        edible_grams_per_package=Decimal("100"),
        package_price=Decimal("1"),
        currency="EUR",
        minimum_order=Decimal(0),
        fulfilment_fee=Decimal(0),
        free_delivery_threshold=None,
        nutrients=(
            CandidateNutrient("ENERCC", EvidenceStatus.KNOWN, Decimal("100")),
            CandidateNutrient("FIBT", EvidenceStatus.KNOWN, Decimal("1")),
            CandidateNutrient("NACL", EvidenceStatus.KNOWN, Decimal("1")),
        ),
        observed_at=NOW,
    )
    return PlanningInputSnapshot(
        household_id="h",
        derivation_date=TODAY,
        market_as_of=NOW,
        standard_version="test",
        policy_version="ADR-007-v1",
        energy_target_kcal=Decimal("100"),
        targets=tuple(targets),
        candidates=(candidate,),
    )


def test_generate_plan_enriches_only_positive_adequacy_gap_after_solver():
    snapshot = _snapshot(
        (
            TargetDimension(
                "FIBT",
                TargetKind.ADEQUACY_FLOOR,
                lower=Decimal("10"),
            ),
            TargetDimension(
                "NACL",
                TargetKind.UPPER_BOUND,
                upper=Decimal("0.5"),
            ),
        )
    )
    source = SuggestionSource(
        {
            "FIBT": (
                TheoreticalFoodCandidate(
                    "theoretical",
                    "Theoretical",
                    "legumes_nuts_seeds",
                    Decimal("10"),
                    Decimal("100"),
                    "food-source",
                    "v1",
                ),
            ),
            "NACL": (
                TheoreticalFoodCandidate(
                    "salt",
                    "Salt",
                    "other_or_composite",
                    Decimal("100"),
                    Decimal("100"),
                    "food-source",
                    "v1",
                ),
            ),
        }
    )

    def solved(_snapshot):
        return SolverDecision((SolverLineDecision("offer", 1, Decimal("100")),))

    plan = generate_purchase_plan(
        snapshot_source=SnapshotSource(snapshot),
        suggestion_source=source,
        solver=solved,
        household_id="h",
        derivation_date=TODAY,
        market_as_of=NOW,
    )

    assert positive_gap_measures(snapshot, plan) == ("FIBT",)
    assert source.calls == ["FIBT"]
    assert tuple(item.base_food_id for item in plan.gap_suggestions) == ("theoretical",)
    suggestion = plan.gap_suggestions[0]
    assert suggestion.measure == "FIBT"
    assert suggestion.source_name == "food-source"
    assert suggestion.source_version == "v1"
