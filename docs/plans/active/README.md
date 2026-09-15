# Active execution

Current product work: define and review the smallest MVP target architecture that preserves accepted S1/S2 semantics.

Lifecycle stage: `S3 Architecture`.
Stage state: `IN_PROGRESS`.
Implementation authorization: `none`.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`; see [`../../problem.md`](../../problem.md).
- S1 Requirements: `PASS`; see [`../../requirements/product-requirements.md`](../../requirements/product-requirements.md).
- S2 Strategic DDD: `PASS` for the MVP scope; see [`../../domain/strategic-model.md`](../../domain/strategic-model.md) and [`../../domain/context-map.md`](../../domain/context-map.md).
- S2 Tactical DDD: `PASS` for the accepted MVP scope; see the tactical owners under `docs/domain/` and ADR-002 through ADR-007.
- accepted Bounded Contexts: `Nutrition Targeting`, `Food Knowledge`, `Market Catalog`, `Purchase Planning`.

## S3 proposal under review

- one deployable modular-monolith application process;
- four context-aligned logical modules preserving the accepted Bounded Context ownership;
- inward dependency direction `infrastructure/adapters -> application -> domain` inside each module;
- one transactional relational database, with every persistence object owned by exactly one context and no direct cross-context table reads/writes;
- cross-context collaboration only through provider-owned application contracts matching the accepted Context Map;
- one immutable Planning Input Snapshot per planning run, assembled through a consistent-read boundary before optimization;
- Purchase Planning persists plan output together with sufficient immutable calculation evidence/provenance;
- optimization runs through an in-process solver adapter owned by Purchase Planning; concrete solver library is deferred to S4;
- synchronous MVP planning; no queue, worker, broker, microservice or distributed transaction without new evidence.

See [`../../architecture/target-architecture.md`](../../architecture/target-architecture.md), [`../../decisions/ADR-008-mvp-modular-monolith-architecture.md`](../../decisions/ADR-008-mvp-modular-monolith-architecture.md) and [`../../decisions/ADR-009-deterministic-planning-execution.md`](../../decisions/ADR-009-deterministic-planning-execution.md).

## Architecture constraints inherited from S2

- provider-owned facts remain authoritative in their contexts;
- active Nutrition Standard Sets and nutrient mappings are versioned/provenanced;
- unknown/trace nutrient evidence cannot become false zero through infrastructure;
- executable market data preserves observation/validity/currency/order conditions;
- Purchase Planning is basket-global and deterministic under ADR-007;
- planned utilized quantity is distinct from purchased package quantity and package surplus;
- member-level safety/allocation guarantees remain outside MVP.

## S3 review gate

Before `PASS`, review the proposal against:

1. semantic ownership and dependency direction;
2. persistence/data-ownership bypass risks;
3. consistency and temporal/version behavior during a planning run;
4. optimizer boundary and deterministic policy preservation;
5. unnecessary infrastructure/distribution/abstraction;
6. ability to select concrete implementation technology in S4 without reopening accepted architecture.

P0/P1 architecture findings keep S3 open. If a finding actually requires missing product behavior or domain semantics, reopen S1/S2 rather than solving it through architecture.

## Explicit S4 choices deferred

- programming language/runtime;
- framework and transport/UI technology;
- relational database vendor and migration/query tooling;
- concrete optimization library;
- deployment hosting/provider.

## Next

Run the architecture review. Resolve any P0/P1 findings in the smallest owning artifact. Mark S3 `PASS` only after the modular-monolith/persistence/snapshot/solver structure is coherent; then open S4 Implementation Readiness for one bounded end-to-end implementation slice.
