# Application Design

Status: accepted for MVP implementation readiness.

## Responsibility

This design translates accepted domain and architecture contracts into application use cases, ports and orchestration. Domain policy remains inside its owning Bounded Context; application code coordinates it without redefining it.

## Primary use case

`GeneratePurchasePlan` is the implementation-facing end-to-end use case.

Inputs:

- `household_id`;
- explicit nutrition `derivation_date`;
- explicit market `as_of` instant.

Output:

- one deterministic Purchase Plan result with selected purchase groups/lines, mapped coverage, unsupported/indeterminate dimensions, safety diagnostics, total acquisition cost and provenance; or
- accepted `no_executable_plan`; or
- a technical application failure distinct from domain outcomes.

Execution:

1. Nutrition Targeting derives the household target for the explicit derivation date and active standard version.
2. Food Knowledge supplies canonical food/nutrient/category facts through provider-owned contracts.
3. Market Catalog supplies executable offers for the explicit market `as_of`.
4. composition captures those provider facts inside one coherent relational read scope and closes that scope.
5. Purchase Planning builds an immutable Planning Input Snapshot.
6. Purchase Planning maps the snapshot into the solver port and accepts only policy-optimal or hard-model-infeasible outcomes.
7. reportable domain facts are recalculated from accepted decision quantities.
8. positive mapped gaps may be enriched with theoretical Food Knowledge suggestions after executable optimization.

No provider read is permitted during solver execution.

## Provider contracts

### Nutrition Targeting → Purchase Planning

Publishes an immutable household-target value containing standard version, derivation date, 30-day energy/target facts, member provenance, member safety limits and explicit target/safety coverage gaps.

### Food Knowledge → Market Catalog / Purchase Planning

Publishes immutable Base Food and nutrient facts. Nutrient evidence preserves the accepted evidence-state vocabulary; only `known` and `zero` are quantitative. Missing measures are represented as missing evidence rather than numeric zero.

For gap enrichment, Food Knowledge exposes candidates by canonical nutrient measure and retains source/category provenance.

### Market Catalog → Purchase Planning

Publishes executable offer facts with SKU/Base Food identity, edible package quantity, effective normalized nutrient facts, merchant/channel conditions, price/currency, availability and observation/validity provenance.

Only executable offers at the requested `as_of` may enter the planning snapshot.

## Purchase Planning ports

Purchase Planning owns:

- snapshot input shape;
- solver problem construction;
- solver status interpretation;
- post-solve domain validation/reporting;
- `GapSuggestionSource` for advisory theoretical alternatives.

The solver is infrastructure. A timeout, cancellation, unknown status, numeric failure or unproven feasible incumbent maps to technical failure, never to `partial`.

## Composition boundary

The composition layer may coordinate one database-consistent read scope across provider persistence adapters because the MVP uses one physical relational store. Database sessions/connections do not cross application contracts.

Cross-context identifiers are opaque values. Consumers never import provider persistence tables or repositories as semantic contracts.

## Transaction boundaries

State-changing imports/commands are context-local transactions.

Plan generation has two phases:

- coherent provider read/capture;
- pure computation/solver execution after the read scope is closed.

No transaction spans solver execution.

## Import use cases

Each provider context owns import/application commands for its data. Import adapters parse external representation and call those commands. They cannot write tables directly or bypass normalization/provenance validation.

## Dependency rule

Allowed direction inside a context:

`adapter/infrastructure → application → domain`.

Cross-context dependencies target provider-owned application contracts only. Domain code has no dependency on SQLAlchemy, Alembic, PySCIPOpt, CLI or Harness.

## Implementation invariant

Any implementation requiring a consumer to query another context's tables, reinterpret provider evidence, keep database state open during optimization, or move business ranking into solver configuration contradicts this accepted design and must reopen the owning upstream decision.
