# MVP Implementation Completion Criteria

Status: accepted for implementation readiness.

Implementation is complete only when all criteria below are evidenced on the implementation revision.

## Build and dependency baseline

- Python/runtime and direct dependencies conform to ADR-010 and the committed lockfile.
- A clean checkout can create the environment, run migrations and execute tests without undocumented manual code changes.
- No unapproved framework, service, queue, broker or second datastore is required.

## Architecture boundaries

- Four accepted Bounded Contexts remain explicit modules in one deployable process.
- Domain modules have no dependency on SQLAlchemy, Alembic, PySCIPOpt, CLI or Harness.
- Cross-context collaboration uses provider-owned application contracts.
- No cross-context table access, relational foreign key or shared business entity bypasses ownership.
- Provider reads finish before solver execution.

Evidence: automated architecture tests plus representative integration tests.

## Product/domain behavior

- household target derivation preserves explicit derivation date, standard version, mappings, provenance and safety semantics;
- nutrient evidence preserves all accepted evidence states and never treats unknown/trace/limit states as numeric zero;
- executable market facts preserve edible quantity, price/currency, availability and temporal/order conditions;
- Purchase Planning implements the complete accepted deterministic ranking and distinguishes full/partial/no-executable-plan semantics from technical failures;
- theoretical suggestions are advisory post-plan enrichment only.

Evidence: bounded-context and application outcome tests.

## Persistence

- migrations create the accepted context-owned relational representation;
- SQLite production settings satisfy ADR-010;
- authoritative decimals round-trip without binary-float authority;
- planning capture uses a coherent file-backed database read scope;
- no durable planning snapshot/history is introduced without an upstream requirement.

Evidence: migration, persistence and snapshot integration tests.

## Solver

- integer/continuous/conditional model semantics implement the accepted planning policy;
- every sequential business objective is proven optimal before a primary plan is accepted;
- hard infeasibility is distinguishable from timeout/unknown/error;
- unfinished feasible incumbents are rejected as technical failure;
- business-equivalent optima resolve through the stable final technical order;
- reportable domain values are recalculated outside solver reporting.

Evidence: solver-policy tests including failure/status cases.

## External contract

The `nutrition-plan` CLI implements the accepted CLI contract:

- four required explicit inputs;
- separate nutrition derivation date and market `as_of`;
- deterministic canonical JSON on success;
- technical failures cannot masquerade as accepted domain outcomes.

Evidence: CLI and end-to-end tests.

## Verification gate

The complete repository test suite passes together with:

- architecture-boundary checks;
- migration/data package integrity checks;
- committed nutrition-standard manifest reproducibility;
- representative end-to-end planning;
- Harness Engineering Graph/Core validation and `IMPLEMENTATION` evaluation.

## Documentation consistency

Accepted requirements, domain design, architecture, application design, data design, interface contract, implementation plan, completion criteria and verification strategy contain no known P0/P1 contradiction.

Implementation discoveries that change semantic decisions are resolved upstream and the affected CanonicalArtifact is updated before completion is claimed.

## Completion result

When every criterion above has passing evidence and Harness evaluates the `IMPLEMENTATION` Consumer as `COMPLETE`, coding work may be considered implementation-complete for the accepted MVP scope. This does not authorize unmodeled BLS production-import work or future product scope.
