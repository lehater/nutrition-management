# Component Design Constraint Experiment

Status: research evidence; not a canonical design artifact.

## Setup

Same accepted Nutrition MVP inputs were reviewed in two modes.

**A — current-guidance mode:** use the accepted architecture/application/data/interface documents and ordinary implementation judgement, without the explicit Engineering Design Policy.

**B — constrained mode:** use the same inputs plus `docs/engineering/engineering-design-policy.md`.

The comparison concerns structural decisions that a coding agent would otherwise be free to make. It does not score prose style.

## A — freedoms left by current guidance

The existing design is sufficient to infer the four context modules and the general inward dependency rule, but several code-level choices remain legitimate:

- `generate_purchase_plan` may accept an untyped duck-typed `snapshot_source` and solver callable;
- coherent snapshot capture may remain a concrete composition object rather than an application-owned port;
- solver abstraction may be represented only by a callable convention;
- provider-contract → Purchase Planning snapshot mapping may remain embedded in the composition adapter;
- application orchestration, infeasibility mapping and post-plan enrichment may remain one function;
- repository classes may be treated as convenient provider APIs in composition because the architecture prohibits only cross-context consumer access, not every concrete dependency at the composition root;
- no artifact requires a complete inventory of public components or abstraction ownership.

All of these can be made to pass the current architecture tests. Therefore current `IMPLEMENTATION COMPLETE` did not uniquely constrain code structure.

## B — consequences of the explicit policy

The policy forces several decisions to become explicit.

### Application-owned planning ports

Purchase Planning application owns three narrow ports:

- `PlanningSnapshotSource.capture(household_id, derivation_date, market_as_of) -> PlanningInputSnapshot`;
- `OptimizationSolver.solve(snapshot) -> SolverDecision`, with `HardModelInfeasible` and `SolverTechnicalFailure` as application-facing failure semantics;
- existing `GapSuggestionSource.candidates_for_measure(measure)`.

This removes the untyped structural freedom around the first two dependencies and makes DIP/LSP/ISP reviewable.

### Composition adapter

The coherent database read implementation is an outer adapter implementing `PlanningSnapshotSource`. It may instantiate provider repositories because composition is explicitly the infrastructure coordination boundary. Purchase Planning application cannot import those repositories.

### Mapping responsibility

Provider application facts are translated to `PlanningInputSnapshot` inside the snapshot adapter through explicit private/pure mapping functions. The mapping is not domain policy and does not belong in provider repositories. This isolates representation translation from transaction coordination without requiring a generic mapper framework.

### Solver adapter

The SCIP implementation implements `OptimizationSolver`. SCIP status/numeric mechanics are translated at this boundary. Purchase Planning application sees only accepted solver decision/failure semantics.

### Use-case orchestration

The public Generate Purchase Plan application service owns orchestration only: capture → solve → build domain plan → post-plan gap enrichment. It does not construct SQL repositories or SCIP models.

A class is not required merely to satisfy Clean Architecture. A function with explicit typed ports remains acceptable under KISS/SRP. A class becomes justified only if construction/lifetime/configuration creates a concrete need.

## Deliberate violation tests

The policy rejects each of these otherwise tempting implementations:

1. Purchase Planning application imports `MarketCatalogRepository` directly — violates DIP and the provider application boundary.
2. Domain `PurchasePlan` carries a SQLAlchemy row/model — violates inward dependency and representation ownership.
3. `ScipSolver` queries Food Knowledge while optimizing — violates snapshot architecture and solver-port contract.
4. One `Repository` interface exposes member profiles, foods, offers and plans — violates ISP and bounded-context ownership.
5. Introduce `AbstractRepository[T]`, event bus and mediator solely for future flexibility — violates YAGNI/OCP interpretation.
6. Add CQRS command/query infrastructure although the accepted MVP has no independent scaling/model requirement — rejected as non-applicable ceremony.
7. Treat CLI HATEOAS/REST rules as mandatory — rejected because the interface is not REST.

## Result

Explicit policy materially reduces structural freedom without requiring a new Harness evaluator state.

The strongest effect comes from **project-owned obligations**, not from the acronym names themselves. `SOLID` alone would not determine that the snapshot source and solver need application-owned ports; the DIP/ISP obligations tied to the accepted architecture do.

The experiment also shows why production-method guidance and project policy should remain separate: GRASP can help discover responsibilities, but the accepted dependency/ownership obligations must persist after the artifact is produced.
