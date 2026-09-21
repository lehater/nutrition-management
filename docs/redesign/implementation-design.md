# Implementation Design — Terminal Pre-Code Baseline

Status: accepted.
Boundary: this is the final design artifact before coding. No implementation code is authorized by this document itself.

## Selected realization

- runtime: Python 3.14;
- packaging/environment: uv-managed Python project with committed lockfile;
- deployment: one local modular-monolith process;
- persistence: file-backed SQLite relational database;
- migration: Alembic;
- ORM/persistence mapping: SQLAlchemy;
- optimization: SCIP through PySCIPOpt;
- first external interface: deterministic CLI;
- automated verification: pytest plus architecture/structure checks.

These are implementation choices, not domain semantics. Replacing one later does not authorize changing upstream contracts.

## Module realization

Create one top-level package with four context-aligned modules:

- nutrition_targeting;
- food_knowledge;
- market_catalog;
- purchase_planning.

Each context separates domain, application and infrastructure/adapters where applicable. A composition module is the only place allowed to select concrete implementations across contexts.

Dependency direction inside each context is infrastructure/adapters → application → domain.

## Persistence realization

Use one SQLite file with context-owned tables and no cross-context foreign keys/ORM relationships. SQLAlchemy mappings remain infrastructure-only. Alembic owns one migration stream but each migration/table has an explicit context owner.

Authoritative Decimal values are stored losslessly (canonical decimal text or exact decimal-capable representation); timestamps are explicit ISO-8601/UTC at persistence boundaries; dates remain dates; currency is explicit.

Planning input capture uses one explicit SQLite coherent read scope spanning provider reads. That scope closes before SCIP execution.

## Application realization

Provider modules expose immutable application values. Cross-context consumers import provider application contracts, never repositories/mappings.

Purchase Planning exposes a Generate Purchase Plan application operation depending on:

- Planning Input Source;
- Optimization Mechanism;
- Gap Suggestion Source.

Use narrow language-native contracts. Python Protocols are appropriate where static structural typing improves clarity, but wrappers/classes are not required for stateless callables.

## Optimization realization

PySCIPOpt is confined to the optimization adapter. The adapter translates the immutable planning input into the accepted deterministic lexicographic optimization policy and translates completion status back to Purchase Planning-owned outcomes/failures.

SCIP types/status objects never cross the adapter. No provider query occurs during solve. Reportable nutrition/cost/variety values are recalculated outside the solver adapter.

## CLI realization

Provide `nutrition-plan` with explicit database path, household id, derivation date and market-as-of instant. It performs parsing, composition invocation and deterministic canonical JSON serialization only.

No current-clock default is permitted for semantic dates/times.

## Imports

External/manual data imports are outer adapters calling provider-owned application commands. They do not write SQLAlchemy tables directly. Validation/normalization/provenance acceptance occurs before canonical provider state is committed.

## Security realization

No network listener or authentication subsystem is introduced for the local MVP. File/database access follows host permissions. Diagnostics avoid full member profiles/planning snapshots by default. Import parsing treats source files as untrusted data and fails before persistence on invalid canonical representation.

## Construction

Use explicit composition/factory functions. A dependency-injection framework is not required. One concrete repository may satisfy several narrow consumer-owned Protocols where appropriate.

## Implementation sequence

1. project/runtime/composition skeleton and structural dependency checks;
2. context-owned persistence/migrations and provider application contracts;
3. Nutrition Targeting;
4. Food Knowledge;
5. Market Catalog;
6. coherent Planning Input Source;
7. Purchase Planning domain/evaluation policy;
8. SCIP optimization adapter;
9. post-plan gap enrichment;
10. deterministic CLI;
11. full verification gate.

A slice is complete only with its applicable canonical Test Design contracts and design-derived verification evidence.

## Decisions forbidden during coding

Coding must not decide:

- new product scope or target semantics;
- new Bounded Context/ownership direction;
- direct cross-context persistence access;
- a new external/network contract;
- durable planning/history state;
- asynchronous/distributed integration;
- alternative result/failure semantics;
- weakening of coherent capture or deterministic optimization completion;
- reinterpretation of nutrient evidence/safety/provenance.

Any such need becomes an upstream Question.

## Ready-for-code criterion

The design is ready for coding when the canonical Engineering Graph requires this Implementation Design, Test Design and Verification Design, all their upstream capabilities are accepted, and IMPLEMENTATION evaluates COMPLETE. This criterion means design-complete/implementation-authorized; it does not mean implementation exists.

## Delivery, migration and rollback contract

### Migration

Before a release that changes persistent representation:

- the required Alembic revision set is part of the release artifact/baseline;
- migration is applied before the new code is allowed to operate on the database;
- migration verification exercises a representative file-backed SQLite database and checks ownership/integrity invariants;
- source/reference-data changes that alter semantic meaning remain distinguishable from schema mechanics and must already be accepted by their semantic owner.

### Release

A backend/CLI release is one coherent versioned application baseline consisting of the locked Python environment, application package, migration set and matching verification baseline.

Release authorization requires:

- the selected Engineering Graph Consumer/scope to be design-complete;
- applicable automated verification and architecture checks to pass;
- no unresolved blocking Question for a required capability;
- the deployed database schema to be at the release's expected migration revision before normal commands execute.

### Rollback

Rollback must not silently reinterpret a database created by a newer incompatible schema.

- code-only rollback is permitted when the current schema is explicitly compatible with the previous application baseline;
- when a migration is not backward-compatible, rollback requires restoration of a pre-migration database backup/snapshot or an explicitly designed reverse/forward-repair migration;
- destructive or semantics-changing migration without a tested recovery path blocks release;
- rollback success is revalidated with the same startup/schema and representative planning checks used for release acceptance.
