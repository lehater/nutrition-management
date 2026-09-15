from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from nutrition_management.purchase_planning.application.ports import HardModelInfeasible
from nutrition_management.purchase_planning.domain.model import PlanOutcome, PurchasePlan
from nutrition_management.purchase_planning.domain.reporting import build_purchase_plan


def generate_purchase_plan(
    *,
    snapshot_source,
    solver,
    household_id: str,
    derivation_date: date,
    market_as_of: datetime,
) -> PurchasePlan:
    snapshot = snapshot_source.capture(household_id, derivation_date, market_as_of)
    try:
        decision = solver(snapshot)
    except HardModelInfeasible:
        return PurchasePlan(
            household_id=snapshot.household_id,
            derivation_date=snapshot.derivation_date,
            market_as_of=snapshot.market_as_of,
            standard_version=snapshot.standard_version,
            policy_version=snapshot.policy_version,
            outcome=PlanOutcome.NO_EXECUTABLE_PLAN,
            lines=(),
            total_cost=Decimal(0),
            currency=None,
            assessments=(),
            safety_diagnostics=(),
            represented_categories=(),
            represented_base_foods=(),
            max_food_energy_share=Decimal(0),
            provenance_offer_ids=(),
        )
    return build_purchase_plan(snapshot, decision)
