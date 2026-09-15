# ADR-009 — Planning runs use immutable input snapshots and an in-process solver adapter

Status: `accepted` for the S3 baseline.

Date: 2026-09-15.

## Context

Purchase Planning consumes authoritative facts from three provider contexts:

- a derived/versioned Household Nutrition Target from Nutrition Targeting;
- canonical food composition/category facts from Food Knowledge;
- time-sensitive executable Product Card/Offer/Fulfilment facts from Market Catalog.

Optimization can take materially longer than ordinary reads. Holding a database transaction or mutable object graph open while solving would couple planning correctness to concurrent edits and persistence behavior. Re-reading provider state during a solve could also mix nutrition/food/market facts from different moments.

The accepted optimization policy is deterministic and auditable. A persisted Purchase Plan therefore needs to retain the exact facts/provenance on which it was calculated even when the current profile, catalog or offers later change.

The optimizer itself is computational infrastructure. It must not become the owner of target semantics, variety semantics, market executability rules or plan outcome meaning.

## Decision

### Planning input capture

A Generate Purchase Plan use case first assembles an immutable **Planning Input Snapshot** through provider-owned application contracts.

The snapshot contains only the facts required by the accepted planning policy, including at least:

- calculation/derivation date and 30-day horizon;
- active Nutrition Standard Set/version and resolved Household Nutrition Target with target-mapping provenance;
- canonical Base Food/Nutrient Measure/category facts required by candidate products and gap suggestions;
- executable Product Card effective nutrient facts and edible package quantities;
- Merchant/Fulfilment Channel/Offer identifiers, price/currency, availability, observed-at and validity/order conditions;
- the accepted optimization-policy version/identity.

The snapshot is a technical immutable calculation input. It does not become authoritative Nutrition Targeting, Food Knowledge or Market Catalog state.

### Consistent-read boundary

Because ADR-008 uses one relational store, snapshot assembly occurs inside one database-consistent read boundary. Provider modules expose published read/application contracts; Purchase Planning does not query provider tables directly.

The consistent read ends after the snapshot has been assembled. Optimization runs only against the immutable snapshot and does not perform provider reads during solving.

### Planning execution record

When a Purchase Plan is persisted, Purchase Planning also persists enough immutable snapshot data/provenance to explain and deterministically re-evaluate that plan even if current upstream state later changes.

This technical record is not profile history, inventory history or market truth. It is evidence for one calculation run.

### Optimizer boundary

Purchase Planning defines an `Optimization Solver` port owned by its application/architecture boundary.

The MVP solver is an **in-process library adapter**, not a network service. The adapter receives a solver-ready problem derived from the immutable snapshot and returns a candidate solution/status.

The concrete solver library is selected in S4. It must support the accepted problem shape, including:

- integer package counts;
- continuous planned-utilized quantities;
- binary/conditional decisions needed for Purchase Groups and bounded variety semantics;
- linearizable commercial conditions such as minimum order, delivery fee and free-delivery threshold;
- deterministic lexicographic/sequential objective evaluation or an equivalent implementation that preserves ADR-007 ordering.

The solver is not allowed to invent business weights that change ADR-007 priority semantics.

### Domain-policy ownership and validation

Purchase Planning code owns transformation from Planning Input Snapshot to solver model and owns interpretation of solver output.

Before persisting/returning a Purchase Plan, application/domain policy revalidates material executable invariants and recalculates reportable coverage/variety/cost facts from the returned quantities rather than trusting solver-specific reporting as authoritative domain truth.

A solver/library failure is a technical execution failure and is distinct from the accepted domain outcome `no_executable_plan`.

### Determinism

For the same Planning Input Snapshot and optimization-policy version, the application must produce the same primary plan/output ordering subject to the accepted stable tie-breakers.

Any solver randomness must be disabled or use a fixed recorded seed. Numeric tolerances used solely for solver mechanics must not change the accepted domain scoring/tolerance semantics.

### Execution mode

The MVP runs plan generation synchronously inside the application process. No queue/worker/job architecture is introduced without measured runtime or product requirements that justify asynchronous execution.

## Consequences

- one planning run never mixes mutable provider facts from different read moments;
- long optimization does not keep a database transaction open;
- persisted plans remain auditable after current profiles/catalog/offers change;
- Purchase Planning remains the owner of optimization semantics while a third-party solver remains replaceable infrastructure;
- no optimizer microservice, message broker or asynchronous worker is required for MVP;
- solver/library selection is a bounded S4 choice constrained by the accepted port/problem shape.

## Alternatives considered

### Query provider modules repeatedly during optimization

Rejected because a solve could observe inconsistent versions/timestamps and become non-reproducible.

### Hold one database transaction for the whole solve

Rejected because optimization may be comparatively long-running and should not extend database locks/snapshots for computational convenience.

### Let the solver library own business scoring and result semantics

Rejected because it would move accepted Purchase Planning policy into infrastructure-specific configuration and make semantic review/audit difficult.

### Run optimization as a separate service or background worker immediately

Rejected because no accepted latency, scale or availability requirement justifies the operational/distributed-systems cost. The solver adapter boundary preserves a later extraction path if evidence appears.

### Persist only the final basket

Rejected because current upstream data is mutable and the product explicitly preserves standard/market provenance. A final basket without its calculation evidence would lose explainability after later edits.

## Supersession

Supersedes: none.
Superseded by: none.
