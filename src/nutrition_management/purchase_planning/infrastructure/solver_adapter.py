from decimal import Decimal, ROUND_HALF_EVEN

from nutrition_management.purchase_planning.application.ports import (
    HardModelInfeasible,
    SolverTechnicalFailure,
)
from nutrition_management.purchase_planning.domain.model import SolverDecision, SolverLineDecision
from nutrition_management.purchase_planning.infrastructure import scip_solver

_QUANTITY_QUANTUM = Decimal("0.000001")
_MECHANICAL_TOLERANCE = Decimal("0.00001")


def _normalize_decision(snapshot, decision: SolverDecision) -> SolverDecision:
    """Remove solver floating noise without changing business tolerances or ordering."""
    candidates = {item.offer_id: item for item in snapshot.candidates}
    normalized = []
    for line in decision.lines:
        candidate = candidates[line.offer_id]
        purchased = candidate.edible_grams_per_package * line.package_count
        quantity = line.planned_grams.quantize(_QUANTITY_QUANTUM, rounding=ROUND_HALF_EVEN)
        if abs(quantity) <= _MECHANICAL_TOLERANCE:
            quantity = Decimal(0)
        if quantity > purchased and quantity - purchased <= _MECHANICAL_TOLERANCE:
            quantity = purchased
        normalized.append(
            SolverLineDecision(
                offer_id=line.offer_id,
                package_count=line.package_count,
                planned_grams=quantity,
            )
        )
    return SolverDecision(lines=tuple(normalized), status=decision.status)


def solve(snapshot):
    try:
        return _normalize_decision(snapshot, scip_solver.solve(snapshot))
    except scip_solver.HardModelInfeasible as exc:
        raise HardModelInfeasible(str(exc)) from exc
    except scip_solver.SolverTechnicalFailure as exc:
        raise SolverTechnicalFailure(str(exc)) from exc
