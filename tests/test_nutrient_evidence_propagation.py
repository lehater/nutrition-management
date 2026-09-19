from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from nutrition_management.food_knowledge.application.contracts import (
    FoodFact,
    NutrientEvidenceStatus,
    NutrientFact,
)
from nutrition_management.food_knowledge.application.imports import import_food
from nutrition_management.food_knowledge.domain.model import NutrientEvidence, NutrientStatus
from nutrition_management.food_knowledge.infrastructure.repository import FoodKnowledgeRepository
from nutrition_management.market_catalog.application.service import executable_market_projection
from nutrition_management.market_catalog.domain.model import (
    Availability,
    FulfilmentChannel,
    FulfilmentMode,
    Offer,
    ProductCard,
)
from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    MemberSafetyLimit,
    PlanningInputSnapshot,
    PurchaseCandidate,
    SolverDecision,
    SolverLineDecision,
    TargetDimension,
    TargetKind,
)
from nutrition_management.purchase_planning.domain.reporting import build_purchase_plan
from nutrition_management.purchase_planning.domain.safety import build_safety_diagnostics
from nutrition_management.purchase_planning.infrastructure import solver_adapter

NOW = datetime(2026, 9, 19, 12, tzinfo=UTC)
TODAY = date(2026, 9, 19)

NON_QUANTITATIVE_APPLICATION_STATUSES = (
    NutrientEvidenceStatus.TRACE,
    NutrientEvidenceStatus.BELOW_QUANTIFICATION_LIMIT,
    NutrientEvidenceStatus.BELOW_DETECTION_LIMIT,
    NutrientEvidenceStatus.BELOW_DETECTION_OR_QUANTIFICATION_LIMIT,
    NutrientEvidenceStatus.MISSING,
)

NON_QUANTITATIVE_PLANNING_STATUSES = (
    EvidenceStatus.TRACE,
    EvidenceStatus.BELOW_QUANTIFICATION_LIMIT,
    EvidenceStatus.BELOW_DETECTION_LIMIT,
    EvidenceStatus.BELOW_DETECTION_OR_QUANTIFICATION_LIMIT,
    EvidenceStatus.MISSING,
)


def _food_with_all_states() -> FoodFact:
    return FoodFact(
        base_food_id="evidence-food",
        name="Evidence Food",
        category="fruit_and_vegetables",
        source_name="evidence-fixture",
        source_version="4.0",
        nutrients=(
            NutrientFact("KNOWN", NutrientEvidenceStatus.KNOWN, Decimal("1.25")),
            NutrientFact("ZERO", NutrientEvidenceStatus.ZERO, Decimal("0")),
            NutrientFact("TRACE", NutrientEvidenceStatus.TRACE, None),
            NutrientFact("LOQ", NutrientEvidenceStatus.BELOW_QUANTIFICATION_LIMIT, None),
            NutrientFact("LOD", NutrientEvidenceStatus.BELOW_DETECTION_LIMIT, None),
            NutrientFact(
                "LOD_OR_LOQ",
                NutrientEvidenceStatus.BELOW_DETECTION_OR_QUANTIFICATION_LIMIT,
                None,
            ),
            NutrientFact("MISSING", NutrientEvidenceStatus.MISSING, None),
        ),
    )


def _planning_candidate(
    offer_id: str,
    *,
    fiber_status: EvidenceStatus,
    fiber_amount: Decimal | None,
    price: Decimal = Decimal("1"),
) -> PurchaseCandidate:
    return PurchaseCandidate(
        offer_id=offer_id,
        sku_id=f"sku-{offer_id}",
        base_food_id=f"food-{offer_id}",
        food_name=f"Food {offer_id}",
        category="fruit_and_vegetables",
        merchant_id="merchant",
        channel_id="channel",
        fulfilment_mode="pickup",
        edible_grams_per_package=Decimal("100"),
        package_price=price,
        currency="EUR",
        minimum_order=Decimal(0),
        fulfilment_fee=Decimal(0),
        free_delivery_threshold=None,
        nutrients=(
            CandidateNutrient("ENERCC", EvidenceStatus.KNOWN, Decimal("100")),
            CandidateNutrient("FIBT", fiber_status, fiber_amount),
        ),
        observed_at=NOW,
    )


def _snapshot(*candidates: PurchaseCandidate) -> PlanningInputSnapshot:
    return PlanningInputSnapshot(
        household_id="h",
        derivation_date=TODAY,
        market_as_of=NOW,
        standard_version="test",
        policy_version="ADR-007-v1",
        energy_target_kcal=Decimal("100"),
        targets=(
            TargetDimension(
                "FIBT",
                TargetKind.ADEQUACY_FLOOR,
                lower=Decimal("10"),
            ),
        ),
        candidates=tuple(candidates),
    )


def test_food_knowledge_domain_models_all_seven_states_without_numeric_fabrication():
    assert {status.value for status in NutrientStatus} == {
        "known",
        "zero",
        "trace",
        "below_quantification_limit",
        "below_detection_limit",
        "below_detection_or_quantification_limit",
        "missing",
    }

    for status in (
        NutrientStatus.TRACE,
        NutrientStatus.BELOW_QUANTIFICATION_LIMIT,
        NutrientStatus.BELOW_DETECTION_LIMIT,
        NutrientStatus.BELOW_DETECTION_OR_QUANTIFICATION_LIMIT,
        NutrientStatus.MISSING,
    ):
        evidence = NutrientEvidence("X", status, None)
        assert evidence.is_quantitatively_known is False
        with pytest.raises(ValueError, match="non-quantitative"):
            NutrientEvidence("X", status, Decimal("0"))


def test_food_knowledge_persistence_round_trips_all_seven_states(engine):
    original = _food_with_all_states()
    with engine.begin() as connection:
        import_food(FoodKnowledgeRepository(connection), original)

    with engine.connect() as connection:
        loaded = FoodKnowledgeRepository(connection).get_food(original.base_food_id)

    assert tuple((item.measure, item.status, item.amount_per_100g) for item in loaded.nutrients) == tuple(
        sorted(
            (
                item.measure,
                item.status,
                item.amount_per_100g,
            )
            for item in original.nutrients
        )
    )


def test_market_catalog_preserves_all_food_knowledge_evidence_states():
    food = _food_with_all_states()
    product = ProductCard("sku", food.base_food_id, "SKU", Decimal("100"))
    channel = FulfilmentChannel(
        "channel",
        "merchant",
        FulfilmentMode.PICKUP,
        "EUR",
        observed_at=NOW,
    )
    offer = Offer(
        "offer",
        "sku",
        "channel",
        Decimal("1"),
        "EUR",
        Availability.AVAILABLE,
        NOW,
    )

    projected = executable_market_projection(
        products=(product,),
        channels=(channel,),
        offers=(offer,),
        food_lookup=lambda _food_id: food,
        as_of=NOW,
    )[0]

    assert tuple((item.measure, item.status, item.amount_per_100g) for item in projected.nutrients) == tuple(
        sorted(
            (
                item.measure,
                item.status,
                item.amount_per_100g,
            )
            for item in food.nutrients
        )
    )


def test_planning_enum_accepts_every_food_knowledge_evidence_state():
    for status in NutrientEvidenceStatus:
        assert EvidenceStatus(status.value).value == status.value


@pytest.mark.parametrize("status", NON_QUANTITATIVE_PLANNING_STATUSES)
def test_reporting_treats_every_non_quantitative_state_as_unknown(status):
    candidate = _planning_candidate(
        "unknown",
        fiber_status=status,
        fiber_amount=None,
    )
    plan = build_purchase_plan(
        _snapshot(candidate),
        SolverDecision((SolverLineDecision("unknown", 1, Decimal("100")),)),
    )

    fiber = next(item for item in plan.assessments if item.measure == "FIBT")
    assert fiber.amount == 0
    assert fiber.unknown_evidence is True
    assert fiber.indeterminate is True
    assert fiber.penalty > 0


@pytest.mark.parametrize("status", NON_QUANTITATIVE_PLANNING_STATUSES)
def test_safety_treats_every_non_quantitative_state_as_indeterminate(status):
    candidate = _planning_candidate(
        "unknown",
        fiber_status=status,
        fiber_amount=None,
    )
    snapshot = _snapshot(candidate)
    snapshot = PlanningInputSnapshot(
        **{
            **snapshot.__dict__,
            "member_safety_limits": (
                MemberSafetyLimit("member", "limit", "FIBT", Decimal("0.1")),
            ),
        }
    )

    diagnostic = build_safety_diagnostics(
        snapshot,
        {"unknown": Decimal("100")},
    )[0]
    assert diagnostic.planned_amount_30d == 0
    assert diagnostic.indeterminate is True
    assert diagnostic.exceeds_period_equivalent is False


@pytest.mark.parametrize("status", NON_QUANTITATIVE_PLANNING_STATUSES)
def test_solver_avoids_non_quantitative_fiber_when_determinate_option_exists(status):
    unknown = _planning_candidate(
        "unknown",
        fiber_status=status,
        fiber_amount=None,
        price=Decimal("0.1"),
    )
    known = _planning_candidate(
        "known",
        fiber_status=EvidenceStatus.KNOWN,
        fiber_amount=Decimal("10"),
        price=Decimal("5"),
    )

    decision = solver_adapter.solve(_snapshot(unknown, known))

    chosen = {item.offer_id for item in decision.lines}
    assert "known" in chosen
    assert "unknown" not in chosen


def test_zero_is_quantitative_and_distinct_from_non_quantitative_states():
    candidate = _planning_candidate(
        "zero",
        fiber_status=EvidenceStatus.ZERO,
        fiber_amount=Decimal("0"),
    )
    plan = build_purchase_plan(
        _snapshot(candidate),
        SolverDecision((SolverLineDecision("zero", 1, Decimal("100")),)),
    )

    fiber = next(item for item in plan.assessments if item.measure == "FIBT")
    assert fiber.amount == 0
    assert fiber.unknown_evidence is False
    assert fiber.indeterminate is False
    assert fiber.penalty > 0
