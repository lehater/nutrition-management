from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from nutrition_management.purchase_planning.application.ports import HardModelInfeasible, SolverTechnicalFailure
from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    PlanningInputSnapshot,
    PurchaseCandidate,
    TargetDimension,
    TargetKind,
)
from nutrition_management.purchase_planning.domain.reporting import build_purchase_plan
from nutrition_management.purchase_planning.infrastructure import scip_solver, solver_adapter

NOW = datetime(2026, 9, 15, 12, tzinfo=UTC)
TODAY = date(2026, 9, 15)


def candidate(
    offer_id: str,
    *,
    sku: str,
    food: str,
    category: str,
    merchant: str,
    channel: str,
    price: str,
    grams: str = "100",
    nutrients=(),
    fee: str = "0",
    threshold: str | None = None,
):
    return PurchaseCandidate(
        offer_id=offer_id,
        sku_id=sku,
        base_food_id=food,
        food_name=food,
        category=category,
        merchant_id=merchant,
        channel_id=channel,
        fulfilment_mode="delivery" if Decimal(fee) else "pickup",
        edible_grams_per_package=Decimal(grams),
        package_price=Decimal(price),
        currency="EUR",
        minimum_order=Decimal(0),
        fulfilment_fee=Decimal(fee),
        free_delivery_threshold=None if threshold is None else Decimal(threshold),
        nutrients=tuple(nutrients),
        observed_at=NOW,
    )


def known(measure: str, amount: str):
    return CandidateNutrient(measure, EvidenceStatus.KNOWN, Decimal(amount))


def missing(measure: str):
    return CandidateNutrient(measure, EvidenceStatus.MISSING, None)


def snapshot(candidates, *, energy="200", targets=()):
    return PlanningInputSnapshot(
        household_id="h",
        derivation_date=TODAY,
        market_as_of=NOW,
        standard_version="test",
        policy_version="ADR-007-v1",
        energy_target_kcal=Decimal(energy),
        targets=tuple(targets),
        candidates=tuple(candidates),
    )


def test_cost_close_prefers_one_group_over_slightly_cheaper_split_purchase():
    food1 = (known("ENERCC", "100"), known("N1", "100"), known("N2", "0"))
    food2 = (known("ENERCC", "100"), known("N1", "0"), known("N2", "100"))
    candidates = (
        candidate("a1", sku="s1", food="f1", category="fruit_and_vegetables", merchant="ma", channel="ca", price="10", nutrients=food1),
        candidate("a2", sku="s2", food="f2", category="legumes_nuts_seeds", merchant="ma", channel="ca", price="10", nutrients=food2),
        candidate("b1", sku="s1", food="f1", category="fruit_and_vegetables", merchant="mb", channel="cb", price="9.8", nutrients=food1),
        candidate("c2", sku="s2", food="f2", category="legumes_nuts_seeds", merchant="mc", channel="cc", price="9.8", nutrients=food2),
    )
    targets = (
        TargetDimension("N1", TargetKind.ADEQUACY_FLOOR, lower=Decimal("100")),
        TargetDimension("N2", TargetKind.ADEQUACY_FLOOR, lower=Decimal("100")),
    )
    snap = snapshot(candidates, targets=targets)
    decision = solver_adapter.solve(snap)
    chosen = {line.offer_id for line in decision.lines}
    assert chosen == {"a1", "a2"}


def test_integer_packages_continuous_planned_quantity_and_free_delivery_threshold():
    item = candidate(
        "offer",
        sku="sku",
        food="food",
        category="grains_cereal_products_potatoes",
        merchant="merchant",
        channel="delivery",
        price="10",
        grams="1000",
        nutrients=(known("ENERCC", "100"),),
        fee="5",
        threshold="15",
    )
    snap = snapshot((item,), energy="1500")
    decision = solver_adapter.solve(snap)
    assert decision.lines[0].package_count == 2
    assert Decimal("1425") - Decimal("0.001") <= decision.lines[0].planned_grams <= Decimal("1575") + Decimal("0.001")
    plan = build_purchase_plan(snap, decision)
    assert plan.total_cost == Decimal("20")
    assert plan.lines[0].surplus_grams > 0


def test_unknown_nutrient_use_is_avoided_before_cost_when_determinate_alternative_exists():
    unknown = candidate(
        "cheap-unknown",
        sku="u",
        food="fu",
        category="fruit_and_vegetables",
        merchant="m",
        channel="c",
        price="1",
        nutrients=(known("ENERCC", "100"), missing("FIBT")),
    )
    determinate = candidate(
        "known",
        sku="k",
        food="fk",
        category="fruit_and_vegetables",
        merchant="m",
        channel="c",
        price="5",
        nutrients=(known("ENERCC", "100"), known("FIBT", "10")),
    )
    snap = snapshot(
        (unknown, determinate),
        energy="100",
        targets=(TargetDimension("FIBT", TargetKind.ADEQUACY_FLOOR, lower=Decimal("10")),),
    )
    decision = solver_adapter.solve(snap)
    assert {line.offer_id for line in decision.lines} == {"known"}


def test_empty_executable_market_is_hard_infeasible():
    with pytest.raises(HardModelInfeasible):
        solver_adapter.solve(snapshot(()))


def test_infrastructure_unknown_or_timeout_cannot_become_partial(monkeypatch):
    def fail(_snapshot):
        raise scip_solver.SolverTechnicalFailure("timeout")

    monkeypatch.setattr(scip_solver, "solve", fail)
    with pytest.raises(SolverTechnicalFailure, match="timeout"):
        solver_adapter.solve(snapshot(()))


def test_business_equivalent_solution_is_repeatable():
    nutrients = (known("ENERCC", "100"),)
    candidates = (
        candidate("offer-a", sku="s", food="f", category="fruit_and_vegetables", merchant="m", channel="c", price="1", nutrients=nutrients),
        candidate("offer-b", sku="s", food="f", category="fruit_and_vegetables", merchant="m", channel="c", price="1", nutrients=nutrients),
    )
    snap = snapshot(candidates, energy="100")
    first = solver_adapter.solve(snap)
    second = solver_adapter.solve(snap)
    assert first == second
