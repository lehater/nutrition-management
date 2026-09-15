from datetime import UTC, date, datetime
from decimal import Decimal

from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    PlanningInputSnapshot,
    PurchaseCandidate,
    SolverDecision,
    SolverLineDecision,
    TargetDimension,
    TargetKind,
)
from nutrition_management.purchase_planning.domain.reporting import build_purchase_plan, target_penalty


def test_typed_penalty_functions():
    assert target_penalty(TargetDimension("x", TargetKind.ADEQUACY_FLOOR, lower=Decimal("10")), Decimal("8")) == Decimal("0.2")
    assert target_penalty(TargetDimension("x", TargetKind.UPPER_BOUND, upper=Decimal("10")), Decimal("12")) == Decimal("0.2")
    assert target_penalty(TargetDimension("x", TargetKind.INTERVAL, lower=Decimal("10"), upper=Decimal("20")), Decimal("15")) == 0
    point = TargetDimension("x", TargetKind.POINT, point=Decimal("100"))
    assert target_penalty(point, Decimal("95")) == 0
    assert target_penalty(point, Decimal("105")) == 0
    assert target_penalty(point, Decimal("90")) > 0


def test_reporting_distinguishes_purchased_planned_and_surplus_and_recalculates_cost():
    candidate = PurchaseCandidate(
        offer_id="offer-1",
        sku_id="sku-1",
        base_food_id="food-1",
        food_name="Food",
        category="fruit_and_vegetables",
        merchant_id="merchant",
        channel_id="channel",
        fulfilment_mode="delivery",
        edible_grams_per_package=Decimal("1000"),
        package_price=Decimal("3"),
        currency="EUR",
        minimum_order=Decimal("5"),
        fulfilment_fee=Decimal("2"),
        free_delivery_threshold=Decimal("10"),
        nutrients=(
            CandidateNutrient("ENERCC", EvidenceStatus.KNOWN, Decimal("100")),
            CandidateNutrient("PROT625", EvidenceStatus.KNOWN, Decimal("10")),
        ),
        observed_at=datetime(2026, 9, 15, 10, tzinfo=UTC),
    )
    snapshot = PlanningInputSnapshot(
        household_id="h",
        derivation_date=date(2026, 9, 15),
        market_as_of=datetime(2026, 9, 15, 12, tzinfo=UTC),
        standard_version="test",
        policy_version="policy",
        energy_target_kcal=Decimal("1500"),
        targets=(TargetDimension("PROT625", TargetKind.ADEQUACY_FLOOR, lower=Decimal("100")),),
        candidates=(candidate,),
    )
    decision = SolverDecision((SolverLineDecision("offer-1", 2, Decimal("1500")),))
    plan = build_purchase_plan(snapshot, decision)
    line = plan.lines[0]
    assert line.purchased_grams == Decimal("2000")
    assert line.planned_grams == Decimal("1500")
    assert line.surplus_grams == Decimal("500")
    assert plan.total_cost == Decimal("8")  # 2 packages + one delivery fee


def test_unknown_selected_nutrient_makes_assessment_indeterminate():
    candidate = PurchaseCandidate(
        offer_id="offer-1",
        sku_id="sku-1",
        base_food_id="food-1",
        food_name="Food",
        category="fruit_and_vegetables",
        merchant_id="merchant",
        channel_id="channel",
        fulfilment_mode="pickup",
        edible_grams_per_package=Decimal("1000"),
        package_price=Decimal("1"),
        currency="EUR",
        minimum_order=Decimal(0),
        fulfilment_fee=Decimal(0),
        free_delivery_threshold=None,
        nutrients=(
            CandidateNutrient("ENERCC", EvidenceStatus.KNOWN, Decimal("100")),
            CandidateNutrient("FIBT", EvidenceStatus.MISSING, None),
        ),
        observed_at=datetime(2026, 9, 15, 10, tzinfo=UTC),
    )
    snapshot = PlanningInputSnapshot(
        "h",
        date(2026, 9, 15),
        datetime(2026, 9, 15, 12, tzinfo=UTC),
        "test",
        "policy",
        Decimal("1000"),
        (TargetDimension("FIBT", TargetKind.ADEQUACY_FLOOR, lower=Decimal("10")),),
        (candidate,),
    )
    plan = build_purchase_plan(snapshot, SolverDecision((SolverLineDecision("offer-1", 1, Decimal("1000")),)))
    fiber = next(item for item in plan.assessments if item.measure == "FIBT")
    assert fiber.indeterminate is True
