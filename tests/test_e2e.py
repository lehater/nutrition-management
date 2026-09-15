from decimal import Decimal

from nutrition_management.adapters.cli.main import canonical_plan_json
from nutrition_management.composition.planning_snapshot import PlanningSnapshotSource
from nutrition_management.purchase_planning.application.service import generate_purchase_plan
from nutrition_management.purchase_planning.domain.model import PlanOutcome
from nutrition_management.purchase_planning.infrastructure.solver_adapter import solve

from fixture_loader import DERIVATION_DATE, HOUSEHOLD_ID, MARKET_AS_OF, load_acceptance_fixture


def test_acceptance_slice_generates_deterministic_mapped_complete_plan(engine):
    load_acceptance_fixture(engine)
    source = PlanningSnapshotSource(engine)

    snapshot = source.capture(HOUSEHOLD_ID, DERIVATION_DATE, MARKET_AS_OF)
    assert len(snapshot.candidates) == 9
    assert "offer-unavailable" not in {item.offer_id for item in snapshot.candidates}
    assert "offer-expired" not in {item.offer_id for item in snapshot.candidates}
    assert len(snapshot.target_member_provenance) == 2
    assert all(item.pal == Decimal("1.6") for item in snapshot.target_member_provenance)
    assert all(item.pal_activity_adjustment_applied is False for item in snapshot.target_member_provenance)

    first = generate_purchase_plan(
        snapshot_source=source,
        solver=solve,
        household_id=HOUSEHOLD_ID,
        derivation_date=DERIVATION_DATE,
        market_as_of=MARKET_AS_OF,
    )
    second = generate_purchase_plan(
        snapshot_source=source,
        solver=solve,
        household_id=HOUSEHOLD_ID,
        derivation_date=DERIVATION_DATE,
        market_as_of=MARKET_AS_OF,
    )

    assert first.outcome == PlanOutcome.MAPPED_COMPLETE
    assert first.lines
    assert len(first.represented_base_foods) >= 8
    assert len(set(first.represented_categories)) >= 4
    assert first.max_food_energy_share <= Decimal("0.25") + Decimal("1e-8")
    assert any(line.surplus_grams > 0 for line in first.lines)
    assert first.target_member_provenance == snapshot.target_member_provenance
    assert canonical_plan_json(first) == canonical_plan_json(second)
