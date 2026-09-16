from datetime import UTC, date, datetime
from decimal import Decimal

from nutrition_management.purchase_planning.application.ports import HardModelInfeasible
from nutrition_management.purchase_planning.application.service import generate_purchase_plan
from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    PlanOutcome,
    PlanningInputSnapshot,
    PurchaseCandidate,
    SolverDecision,
    SolverLineDecision,
    TargetCoverageGap,
)

NOW = datetime(2026, 9, 15, 12, tzinfo=UTC)
TODAY = date(2026, 9, 15)


class SnapshotSource:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def capture(self, household_id, derivation_date, market_as_of):
        assert household_id == self.snapshot.household_id
        assert derivation_date == self.snapshot.derivation_date
        assert market_as_of == self.snapshot.market_as_of
        return self.snapshot


def _snapshot(candidates=(), target_coverage_gaps=()):
    return PlanningInputSnapshot(
        household_id="h",
        derivation_date=TODAY,
        market_as_of=NOW,
        standard_version="test",
        policy_version="ADR-007-v1",
        energy_target_kcal=Decimal("100"),
        targets=(),
        candidates=tuple(candidates),
        target_coverage_gaps=tuple(target_coverage_gaps),
    )


def _coverage_gap():
    return TargetCoverageGap(
        member_id="member",
        family_id="family",
        state="unsupported_mapping",
        reason="no exact mapping",
    )


def test_hard_infeasible_maps_to_no_executable_plan_and_preserves_target_coverage():
    gap = _coverage_gap()
    snapshot = _snapshot(target_coverage_gaps=(gap,))

    def infeasible(_snapshot):
        raise HardModelInfeasible("no executable basket")

    plan = generate_purchase_plan(
        snapshot_source=SnapshotSource(snapshot),
        solver=infeasible,
        household_id="h",
        derivation_date=TODAY,
        market_as_of=NOW,
    )

    assert plan.outcome == PlanOutcome.NO_EXECUTABLE_PLAN
    assert plan.lines == ()
    assert plan.total_cost == 0
    assert plan.target_coverage_gaps == (gap,)


def test_policy_optimal_basket_with_variety_gap_is_partial_and_preserves_target_coverage():
    candidate = PurchaseCandidate(
        offer_id="offer",
        sku_id="sku",
        base_food_id="food",
        food_name="food",
        category="fruit_and_vegetables",
        merchant_id="merchant",
        channel_id="pickup",
        fulfilment_mode="pickup",
        edible_grams_per_package=Decimal("100"),
        package_price=Decimal("1"),
        currency="EUR",
        minimum_order=Decimal(0),
        fulfilment_fee=Decimal(0),
        free_delivery_threshold=None,
        nutrients=(CandidateNutrient("ENERCC", EvidenceStatus.KNOWN, Decimal("100")),),
        observed_at=NOW,
    )
    gap = _coverage_gap()
    snapshot = _snapshot((candidate,), target_coverage_gaps=(gap,))

    def solved(_snapshot):
        return SolverDecision((SolverLineDecision("offer", 1, Decimal("100")),))

    plan = generate_purchase_plan(
        snapshot_source=SnapshotSource(snapshot),
        solver=solved,
        household_id="h",
        derivation_date=TODAY,
        market_as_of=NOW,
    )

    assert plan.outcome == PlanOutcome.PARTIAL
    assert plan.assessments[0].penalty == 0
    assert plan.represented_base_foods == ("food",)
    assert plan.target_coverage_gaps == (gap,)
