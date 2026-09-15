class SolverTechnicalFailure(RuntimeError):
    """Infrastructure could not prove an accepted domain-relevant solver outcome."""


class HardModelInfeasible(RuntimeError):
    """The correctly constructed hard executability model has no non-empty solution."""
