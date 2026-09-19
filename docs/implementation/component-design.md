# MVP Component Design

Status: research candidate.

Normative constraints: `docs/engineering/engineering-design-policy.md`.

## Purpose

Fix the public component responsibilities, ports and dependency directions required to implement the accepted MVP without leaving architectural decomposition to the coding agent. Private helper functions and local algorithms remain implementation freedom.

## Global dependency structure

```text
CLI adapter
   ↓
composition root ───────────────┐
   ↓ constructs                 │
Generate Purchase Plan          │
   ↓                            │
Purchase Planning application-owned ports
   ↑ implemented by             │
   ├─ SQLite Planning Snapshot Adapter ──→ provider application services/repositories
   ├─ SCIP Optimization Adapter ─────────→ PySCIPOpt/SCIP
   └─ Food Knowledge Gap Suggestion Adapter
                                │
application services ───────────┘
   ↓
domain policy/models
```

Domain has no outward dependency. Application has no dependency on infrastructure.

## Purchase Planning

### Application components

#### `generate_purchase_plan`

Owner: Purchase Planning application.

Responsibility: orchestrate one complete planning use case.

Inputs:

- `PlanningSnapshotSource`;
- `OptimizationSolver`;
- `GapSuggestionSource`;
- household id;
- derivation date;
- market as-of instant.

Flow:

1. capture immutable `PlanningInputSnapshot`;
2. invoke `OptimizationSolver`;
3. map `HardModelInfeasible` to accepted `NO_EXECUTABLE_PLAN`;
4. for a decision, invoke domain reporting to build the plan;
5. determine positive mapped gaps;
6. request/rank theoretical suggestions;
7. return immutable `PurchasePlan`.

It does not construct repositories, open database connections, import SCIP, or implement coverage/ranking calculations.

A function is the preferred representation for the first slice. Do not introduce a use-case class unless state/lifetime requirements appear.

#### `PlanningSnapshotSource` port

Owner: Purchase Planning application.

Contract:

```python
class PlanningSnapshotSource(Protocol):
    def capture(
        self,
        household_id: str,
        derivation_date: date,
        market_as_of: datetime,
    ) -> PlanningInputSnapshot: ...
```

Guarantees: returned snapshot is immutable, internally coherent for one provider read point, market_as_of is explicit/timezone-aware, and no provider read remains open after return.

#### `OptimizationSolver` port

Owner: Purchase Planning application.

Contract:

```python
class OptimizationSolver(Protocol):
    def __call__(self, snapshot: PlanningInputSnapshot) -> SolverDecision: ...
```

Application-facing failures:

- `HardModelInfeasible`;
- `SolverTechnicalFailure`.

No SCIP-specific status/type crosses this port.

#### `GapSuggestionSource` port

Retain the existing narrow contract. It supplies theoretical candidates for one canonical measure and has no market/planning mutation operation.

### Domain components

Keep domain policy as pure functions/value models rather than introducing service classes without state.

Public responsibilities:

- planning model/value types: `PlanningInputSnapshot`, `PurchaseCandidate`, target/evidence/safety value types;
- solver-independent decision types: `SolverDecision`, `SolverLineDecision`;
- reporting: construct/recalculate `PurchasePlan` from snapshot + accepted decision;
- safety evaluation;
- gap detection and theoretical suggestion ranking;
- deterministic business policy helpers used to construct/evaluate the optimization model.

Domain modules must not import application ports.

### Infrastructure components

#### SCIP solver adapter

The existing `solve(snapshot)` function implements the callable `OptimizationSolver` port. A wrapper class is not required.

Responsibilities:

- translate `PlanningInputSnapshot` into SCIP variables/constraints/objective stages;
- run accepted sequential objectives to proven optimality;
- apply final technical tie resolution;
- normalize mechanical floating noise;
- translate SCIP status into application-owned decision/failure semantics.

It does not calculate authoritative report values and does not query provider state.

Prefer a stateless object or function-backed adapter; no inheritance hierarchy is required.

## Coherent snapshot composition

### `SqlitePlanningSnapshotSource`

Outer composition/infrastructure adapter implementing Purchase Planning's `PlanningSnapshotSource`.

Responsibilities:

1. validate/normalize explicit market_as_of;
2. open one SQLite connection/read transaction;
3. instantiate provider persistence adapters on that connection;
4. call provider application services;
5. translate provider application facts into Purchase Planning snapshot value types;
6. close/rollback the read scope;
7. return the immutable snapshot.

The transaction never spans solver execution.

Mapping is implemented as small explicit pure functions local to this adapter (target fact → target dimensions/provenance; executable offer fact → purchase candidate). Do not introduce a generic mapping framework.

## Nutrition Targeting

### Application service

`derive_household_target_fact(repository_port, household_id, derivation_date) -> HouseholdTargetFact`.

Responsibility: orchestrate active standard/profile retrieval and domain derivation; publish the provider-owned immutable application contract.

### Persistence port boundary

For implementation readiness, Nutrition Targeting application code must depend only on the minimal operations it requires from its persistence collaborator. If the existing concrete repository is passed directly today, implementation work should extract a narrow application-owned Protocol when required to remove an application→infrastructure dependency.

The port contains only operations used by targeting application services (profiles/active standard and explicit import/activation operations for their respective use cases); do not create a generic CRUD repository.

### `SqlAlchemyNutritionTargetingRepository`

Infrastructure implementation of the targeting persistence contract. Owns SQLAlchemy table mapping and Decimal/date/source representation translation.

## Food Knowledge

### Provider application contracts

`FoodFact`, `NutrientFact`, `NutrientEvidenceStatus` remain provider-owned immutable contracts.

### Persistence component

`SqlAlchemyFoodKnowledgeRepository` owns Base Food/nutrient persistence mapping. Its public operations remain food-knowledge-specific; no generic repository base class.

### Gap suggestion adapter

`FoodKnowledgeGapSuggestionSource` implements Purchase Planning's `GapSuggestionSource` at the composition boundary using Food Knowledge provider operations/contracts. Purchase Planning never imports the Food Knowledge repository.

## Market Catalog

### Application service

`executable_market_projection(..., as_of) -> tuple[ExecutableOfferFact, ...]`.

Responsibility: apply Market Catalog-owned executability/effective nutrient semantics and publish provider-owned immutable offer facts.

### Persistence component

`SqlAlchemyMarketCatalogRepository` owns Product Card, channel and offer persistence mapping. Cross-context Base Food identity remains opaque; Food Knowledge facts enter Market Catalog application logic through its provider-facing contract/callback, not table access.

## CLI and composition root

### `nutrition_management.adapters.cli.main`

Responsibility only:

- parse the four accepted arguments;
- call composition factory;
- invoke Generate Purchase Plan;
- canonicalize/print JSON;
- return process status.

It contains no SQL query, target derivation, solver policy or domain ranking.

### Composition factory

A composition module owns concrete construction:

- SQLite engine/configuration;
- `SqlitePlanningSnapshotSource`;
- SCIP `solve` adapter;
- `FoodKnowledgeGapSuggestionSource`;
- invocation dependencies for Generate Purchase Plan.

No DI framework is introduced.

## Import components

Each context's import adapter parses external representation into context-owned application import records/commands. Application import service validates/normalizes and calls its context persistence port. Direct table-writing import scripts are forbidden.

BLS production import remains outside this MVP component-design authorization unless its separate Harness consumer becomes ready.

## Construction and ownership matrix

| Consumer | Contract depended on | Contract owner | Concrete implementation selected by |
| --- | --- | --- | --- |
| CLI | Generate Purchase Plan application API | Purchase Planning | composition |
| Generate Purchase Plan | PlanningSnapshotSource | Purchase Planning application | composition |
| Generate Purchase Plan | OptimizationSolver | Purchase Planning application | composition |
| Generate Purchase Plan | GapSuggestionSource | Purchase Planning application | composition |
| Snapshot adapter | Nutrition Targeting published application API | Nutrition Targeting | snapshot composition |
| Snapshot adapter | Food Knowledge published application API | Food Knowledge | snapshot composition |
| Snapshot adapter | Market Catalog published application API | Market Catalog | snapshot composition |
| OptimizationSolver port | solver decision/failure semantics | Purchase Planning | SCIP adapter |
| provider application services | narrow persistence ports | owning provider application | composition/import adapter |

## Forbidden dependencies

- any domain module → application/infrastructure/composition/adapter/framework;
- any application module → its own infrastructure module;
- consumer context → another context's infrastructure/repository/table;
- Purchase Planning solver adapter → provider repositories;
- provider repository → consumer domain model;
- CLI → context repositories or SCIP;
- domain/application public contracts → SQLAlchemy/PySCIPOpt types;
- generic repository/service/event-bus abstractions introduced without an accepted current use.

## Structural verification additions

Architecture tests should verify:

- Purchase Planning application ports exist and infrastructure/composition implementations conform structurally;
- application modules do not import infrastructure;
- provider repositories are not imported by consumer context packages;
- domain modules remain framework-free;
- solver adapter imports no provider infrastructure;
- CLI imports composition/application surface only;
- no cross-context foreign keys.

Behavioral tests provide LSP evidence by running application use cases against fakes for the narrow ports and against concrete adapters in integration tests.

## Implementation freedoms

The coding agent may choose:

- private helper names and decomposition;
- local comprehensions/iteration structure;
- exact module split for pure domain helpers where dependency direction is unchanged;
- whether a stateless adapter is represented by a function or trivial class when the public Protocol remains satisfied;
- test helper/fixture organization.

The coding agent may not change public responsibilities, abstraction ownership, dependency direction, failure semantics or introduce new architectural seams without reopening Component Design.
