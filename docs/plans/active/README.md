# Active execution

Current product work: MVP target architecture is accepted; the next lifecycle step is S4 Implementation Readiness.

Lifecycle stage: `S3 Architecture`.
Stage state: `PASS`.
Implementation authorization: `none`.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`; see [`../../problem.md`](../../problem.md).
- S1 Requirements: `PASS`; see [`../../requirements/product-requirements.md`](../../requirements/product-requirements.md).
- S2 Strategic/Tactical Domain Design: `PASS` for the accepted MVP scope; see `docs/domain/` and ADR-002 through ADR-007.
- accepted Bounded Contexts: `Nutrition Targeting`, `Food Knowledge`, `Market Catalog`, `Purchase Planning`.

## Accepted S3 architecture

- one deployable modular-monolith application process;
- four context-aligned logical modules preserving accepted semantic ownership;
- inward dependency direction `infrastructure/adapters -> application -> domain` inside each module;
- one transactional relational database, with every persistence object owned by exactly one context and no direct cross-context table/ORM reads or writes;
- cross-context collaboration only through provider-owned application contracts matching the accepted Context Map;
- one ephemeral immutable Planning Input Snapshot per executable-basket optimization, assembled through one infrastructure-managed consistent-read scope;
- Purchase Planning returns the plan/provenance required by S2 but does not introduce saved plan history or persist the complete candidate snapshot in MVP;
- theoretical Food Knowledge gap suggestions are post-optimization enrichment and cannot change executable-plan selection/outcome;
- optimization runs through an in-process solver adapter owned by Purchase Planning;
- a domain plan is returned only after the full ADR-007 policy is proven optimal for the snapshot, or hard-model infeasibility is proven;
- a stable technical order resolves remaining business-equivalent optima only after all ADR-007 business criteria;
- synchronous MVP planning; no queue, worker, broker, microservice or distributed transaction without new evidence.

Canonical architecture: [`../../architecture/target-architecture.md`](../../architecture/target-architecture.md).

Consequential architecture decisions:
- [`ADR-008`](../../decisions/ADR-008-mvp-modular-monolith-architecture.md) — modular monolith and context-owned relational persistence;
- [`ADR-009`](../../decisions/ADR-009-deterministic-planning-execution.md) — immutable calculation snapshot, consistent-read coordination, in-process solver boundary and deterministic completion semantics.

## S3 review result

Architecture review against accepted requirements/domain ownership and the Harness architecture-review lenses found no remaining P0/P1 issue for the accepted MVP scope.

Resolved during review:
- **P1** — rejected durable full Planning Input Snapshot / saved-plan architecture because plan history and exact historical replay are not accepted requirements; snapshot is now ephemeral and result provenance remains in the returned plan;
- **P1** — eliminated arbitrary solver selection among fully tied baskets through a final non-business stable technical order;
- **P1** — prohibited returning a merely feasible timeout incumbent as `partial`; `partial` requires completed policy optimization, while unfinished solver execution is a technical failure.

Non-blocking S4 verification risks:
- **P2** — measure actual synchronous optimization runtime on realistic MVP data; if acceptable completion cannot be achieved, reopen S3 before adding asynchronous execution;
- **P2** — select a relational database/transaction strategy that can provide the required coherent read snapshot without leaking session objects through application/domain contracts;
- **P2** — select/configure a solver that can prove every sequential ADR-007 objective stage and the final technical tie order with deterministic numeric behavior.

## Explicit S4 choices deferred

- programming language/runtime;
- application/framework and external transport/UI adapter;
- relational database vendor and migration/query tooling;
- concrete optimization library;
- package/module layout details that realize the four accepted context modules;
- testing strategy and executable architecture-boundary checks;
- deployment hosting/provider.

## Next

Open S4 Implementation Readiness. Choose the smallest concrete stack and one bounded end-to-end vertical slice that can validate the architecture: current profile + standard data -> derived household target -> canonical food/market candidate snapshot -> solver -> one Purchase Plan result with provenance. Define acceptance tests and architecture-boundary checks before authorizing implementation.
