from __future__ import annotations

from typing import Protocol

from nutrition_management.purchase_planning.domain.model import TheoreticalFoodCandidate


class SolverTechnicalFailure(RuntimeError):
    """Infrastructure could not prove an accepted domain-relevant solver outcome."""


class HardModelInfeasible(RuntimeError):
    """The correctly constructed hard executability model has no non-empty solution."""


class GapSuggestionSource(Protocol):
    def candidates_for_measure(
        self,
        measure: str,
    ) -> tuple[TheoreticalFoodCandidate, ...]: ...
