# ADR-009 — Planning runs use immutable input snapshots and an in-process solver adapter

Status: `accepted` for the S3 baseline.

Date: 2026-09-15.

## Context

Purchase Planning consumes authoritative facts from three provider contexts:

- a derived/versioned Household Nutrition Target from Nutrition Targeting;
- canonical food composition/category facts from Food Knowledge;
- time-sensitive executable Product Card/Offer/Fulfilment facts from Market Catalog.

Optimization can take materially longer than ordinary reads. Holding a database transaction or mutable object graph open while solving would couple planning correctness to concurrent edits and persistence behavior. Re-reading provider state during a solve could also mix nutrition/food/market facts from different moments.

The accepted optimization policy is deterministic for one fixed set of calculation inputs. The product requires provenance in the returned Purchase Plan, but it does **not** currently require saved plan history or exact historical replay of every candidate considered by an old calculation.

The optimizer itself is computational infrastructure. It must not become the owner of target semantics, variety semantics, market executability rules or plan outcome meaning.

## Decision

### Planning input capture

A Generate Purchase Plan use case first assembles an immutable **Planning Input Snapshot** through provider-owned application contracts.

The snapshot contains the facts required to choose an executable basket under the accepted planning policy, including at least:

- calculation/derivation date and 30-day horizon;
- active Nutrition Standard Set/version and resolved Household Nutrition Target with target-mapping provenance;
- canonical Base Food/Nutrient Measure/category facts required by executable candidate products;
- executable Product Card effective nutrient facts and edible package quantities;
- Merchant/Fulfilment Channel/Offer identifiers, price/currency, availability, observed-at and validity/order conditions;
- the accepted optimization-policy version/identity.

The snapshot is a technical immutable calculation input with the lifetime of one planning execution. It does not become authoritative Nutrition Targeting, Food Knowledge or Market Catalog state and is not required to be persisted in the MVP.

### Consistent-read boundary

Because ADR-008 uses one relational store, snapshot assembly occurs inside one database-consistent read scope.

The application composition/infrastructure layer owns that read-consistency scope. Provider application contracts remain persistence-agnostic; their persistence adapters participate in the same read snapshot without exposing database transaction/session objects through domain or cross-context contracts.

Purchase Planning does not query provider tables directly.

The consistent read ends after the optimization snapshot has been assembled. Optimization runs only against the immutable snapshot and does not perform provider reads during solving.

### Returned result and provenance

The MVP returns one Purchase Plan result; it does not require persistent plan history.

The returned plan carries the accepted provenance needed to interpret it, including standards/policy identity, calculation date, selected food/SKU/Offer/Fulfilment facts and their relevant source/observation metadata, plus unsupported/indeterminate diagnostics.

Exact replay of an old optimization against the complete historical candidate universe is outside current requirements. If saved-plan history or audit replay becomes product behavior, S1/S2/S3 must be revisited rather than silently turning the ephemeral snapshot into durable authoritative-looking state.

### Gap-suggestion enrichment

Theoretical Base Food suggestions do not affect executable basket selection or Purchase Plan outcome classification.

After the solver result and mapped gaps are known, Purchase Planning may request theoretical gap suggestions from Food Knowledge through its published contract. That enrichment records the Food Knowledge source/provenance used for the suggestions. It is not part of the executable-market optimization snapshot and therefore does not force the complete theoretical food catalog into every solver input.

### Optimizer boundary

Purchase Planning defines an `Optimization Solver` port owned by its application/architecture boundary.

The MVP solver is an **in-process library adapter**, not a network service. The adapter receives a solver-ready problem derived from the immutable snapshot and returns a solution/status.

The concrete solver library is selected in S4. It must support the accepted problem shape, including:

- integer package counts;
- continuous planned-utilized quantities;
- binary/conditional decisions needed for Purchase Groups and bounded variety semantics;
- linearizable commercial conditions such as minimum order, delivery fee and free-delivery threshold;
- lexicographic/sequential objective evaluation that can prove completion of the accepted ADR-007 ordering for the returned primary plan.

The solver is not allowed to invent business weights that change ADR-007 priority semantics.

### Accepted solver outcomes

The application accepts only these solver outcomes as domain-relevant:

- **policy-optimal** — all hard constraints and every sequential/lexicographic business objective stage are completed, including the final technical tie resolution;
- **hard-model-infeasible** — the accepted hard executability model has no non-empty solution and can therefore map to `no_executable_plan`.

`unknown`, numeric failure, adapter failure, cancellation or timeout before policy optimality is established is a **technical execution failure**.

A feasible incumbent returned on timeout is not sufficient for the primary MVP recommendation because it may violate the accepted global/lexicographic ranking even when it satisfies hard constraints. Such an incumbent must not be relabeled as `partial`; `partial` describes the best policy-optimal executable basket with nutritional/variety gaps, not an unfinished optimization process.

### Domain-policy ownership and validation

Purchase Planning code owns transformation from Planning Input Snapshot to solver model and owns interpretation of solver output.

Before returning a Purchase Plan, application/domain policy revalidates material executable invariants and recalculates reportable coverage/variety/cost facts from the returned quantities rather than trusting solver-specific reporting as authoritative domain truth.

A solver/library failure is distinct from the accepted domain outcome `no_executable_plan`.

### Determinism and final technical tie resolution

For the same Planning Input Snapshot and optimization-policy version, the application must produce the same primary plan/output ordering subject to the accepted business ranking.

ADR-007 business criteria can still leave two distinct baskets completely tied after package-surplus mass. When that happens, and only after all accepted business criteria are equal, the application applies a stable **technical** total order over the solution decision vector using immutable provider identifiers and normalized quantities.

This technical ordering carries no claim that one tied product/merchant is better than another. It exists only to choose one reproducible primary recommendation among business-equivalent solutions and must never outrank an ADR-007 business dimension.

The exact canonical serialization/comparison of that decision vector is an S4 detail, but it must be stable for the same snapshot.

Any solver randomness must be disabled or use a fixed execution seed. Numeric tolerances used solely for solver mechanics must not change the accepted domain scoring/tolerance semantics.

### Execution mode

The MVP runs plan generation synchronously inside the application process. No queue/worker/job architecture is introduced without measured runtime or product requirements that justify asynchronous execution.

## Consequences

- one optimization run never mixes mutable provider facts from different read moments;
- optimization does not keep a database read scope open;
- snapshot consistency is implemented without leaking persistence/session objects into domain or cross-context contracts;
- no full-catalog historical snapshot or saved-plan subsystem is introduced without a product requirement;
- theoretical suggestion enrichment remains lightweight and cannot affect executable-plan selection retroactively;
- Purchase Planning remains the owner of optimization semantics while a third-party solver remains replaceable infrastructure;
- business-equivalent solver optima resolve to one reproducible primary recommendation without adding a hidden business preference;
- an unfinished solver run cannot masquerade as the accepted best partial plan;
- no optimizer microservice, message broker or asynchronous worker is required for MVP;
- solver/library selection is a bounded S4 choice constrained by the accepted port/problem shape.

## Alternatives considered

### Query provider modules repeatedly during optimization

Rejected because a solve could observe inconsistent versions/timestamps and become non-deterministic for one logical run.

### Hold one database transaction for the whole solve

Rejected because optimization may be comparatively long-running and should not extend database locks/snapshots for computational convenience.

### Persist the complete Planning Input Snapshot for every run

Rejected for MVP because saved-plan history/exact replay is not an accepted requirement and the candidate snapshot may duplicate a large food/catalog dataset. The returned plan already carries the provenance required by S2.

### Put the complete theoretical food catalog in the solver snapshot for gap suggestions

Rejected because theoretical suggestions are post-plan advisory enrichment and do not affect executable basket selection. Fetching them after gaps are known is smaller and preserves the Food Knowledge boundary.

### Let the solver choose arbitrarily among business-equivalent optima

Rejected because the MVP produces one primary recommendation and the accepted policy is intended to be deterministic. A final technical order is harmless only after every business criterion is equal.

### Return a feasible timeout incumbent as `partial`

Rejected because `partial` is a domain quality outcome after completed policy optimization, not a solver-progress state. Returning an unproven incumbent would weaken the accepted global deterministic policy without an upstream requirement.

### Let the solver library own business scoring and result semantics

Rejected because it would move accepted Purchase Planning policy into infrastructure-specific configuration and make semantic review/audit difficult.

### Run optimization as a separate service or background worker immediately

Rejected because no accepted latency, scale or availability requirement justifies the operational/distributed-systems cost. The solver adapter boundary preserves a later extraction path if evidence appears.

## Supersession

Supersedes: none.
Superseded by: none.
