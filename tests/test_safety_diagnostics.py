from datetime import UTC, date, datetime
from decimal import Decimal

from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    MemberSafetyLimit,
    PlanningInputSnapshot,
    PurchaseCandidate,
)
from nutrition_management.purchase_planning.domain.safety import build_safety_diagnostics

NOW = datetime(2026, 9, 15, 12, tzinfo=UTC)


def _candidate(offer_id: str, status: EvidenceStatus, amount: Decimal | None) -> PurchaseCandidate:
    return PurchaseCandidate(
        offer_id=offer_id,
        sku_id=f"sku-{offer_id}",
        base_food_id=f"food-{offer_id}",
        food_name=f"food-{offer_id}",
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
        nutrients=(CandidateNutrient("NA", status, amount),),
        observed_at=NOW,
    )


def _snapshot(*candidates: PurchaseCandidate) -> PlanningInputSnapshot:
    return PlanningInputSnapshot(
        household_id="h",
        derivation_date=date(2026, 9, 15),
        market_as_of=NOW,
        standard_version="test",
        policy_version="ADR-007-v1",
        energy_target_kcal=Decimal("100"),
        targets=(),
        candidates=tuple(candidates),
        member_safety_limits=(
            MemberSafetyLimit("m1", "limit-1", "NA", Decimal("0.10")),
            MemberSafetyLimit("m2", "limit-2", "NA", Decimal("0.10")),
        ),
    )


def test_safety_limit_is_only_aggregate_period_equivalent_diagnostic():
    snapshot = _snapshot(_candidate("known", EvidenceStatus.KNOWN, Decimal("10")))
    diagnostic = build_safety_diagnostics(snapshot, {"known": Decimal("100")})[0]

    assert diagnostic.planned_amount_30d == Decimal("10")
    assert diagnostic.aggregate_period_equivalent_limit == Decimal("6.00")
    assert diagnostic.exceeds_period_equivalent is True
    assert diagnostic.indeterminate is False
    assert diagnostic.allocation_guarantee is False


def test_unknown_safety_contribution_never_becomes_false_safe_claim():
    snapshot = _snapshot(_candidate("unknown", EvidenceStatus.MISSING, None))
    diagnostic = build_safety_diagnostics(snapshot, {"unknown": Decimal("100")})[0]

    assert diagnostic.indeterminate is True
    assert diagnostic.exceeds_period_equivalent is False
    assert diagnostic.allocation_guarantee is False


def test_known_contribution_can_prove_exceedance_even_when_total_is_indeterminate():
    snapshot = _snapshot(
        _candidate("known", EvidenceStatus.KNOWN, Decimal("10")),
        _candidate("unknown", EvidenceStatus.MISSING, None),
    )
    diagnostic = build_safety_diagnostics(
        snapshot,
        {"known": Decimal("100"), "unknown": Decimal("100")},
    )[0]

    assert diagnostic.planned_amount_30d == Decimal("10")
    assert diagnostic.indeterminate is True
    assert diagnostic.exceeds_period_equivalent is True
    assert diagnostic.allocation_guarantee is False
