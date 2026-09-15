from nutrition_management.purchase_planning.application.ports import (
    HardModelInfeasible,
    SolverTechnicalFailure,
)
from nutrition_management.purchase_planning.infrastructure import scip_solver


def solve(snapshot):
    try:
        return scip_solver.solve(snapshot)
    except scip_solver.HardModelInfeasible as exc:
        raise HardModelInfeasible(str(exc)) from exc
    except scip_solver.SolverTechnicalFailure as exc:
        raise SolverTechnicalFailure(str(exc)) from exc
