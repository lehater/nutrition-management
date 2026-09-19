from __future__ import annotations

from datetime import date, datetime
from typing import Protocol

from nutrition_management.purchase_planning.domain.model import (
    PlanningInputSnapshot,
    SolverDecision,
    TheoreticalFoodCandidate,
)


class SolverTechnicalFailure(RuntimeError):
    """Infrastructure could not prove an accepted domain-relevant solver outcome."""


class HardModelInfeasible(RuntimeError):
    """The correctly constructed hard executability model has no non-empty solution."""


class PlanningSnapshotSource(Protocol):
    def capture(
        self,
        household_id: str,
        derivation_date: date,
        market_as_of: datetime,
    ) -> PlanningInputSnapshot: ...


class OptimizationSolver(Protocol):
    def __call__(self, snapshot: PlanningInputSnapshot) -> SolverDecision: ...


class GapSuggestionSource(Protocol):
    def candidates_for_measure(
        self,
        measure: str,
    ) -> tuple[TheoreticalFoodCandidate, ...]: ...
