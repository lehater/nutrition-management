# ADR-010 — First implementation slice uses Python, SQLite and SCIP

Status: `accepted` for the first implementation slice.

Date: 2026-09-15.
Lifecycle owner: `S4 Implementation Readiness`.

## Context

S3 accepts one modular-monolith process, one relational store, context-owned persistence, an ephemeral coherent-read Planning Input Snapshot and an in-process mixed-integer optimization adapter.

The first implementation slice should validate those constraints with the least operational/tooling surface. There is no accepted requirement for an HTTP API, browser UI, multi-host database, background worker or production hosting topology yet.

The optimization model needs both integer package counts and continuous planned-utilized quantities. It also contains conditional logic for Purchase Groups and material variety representation. A solver requiring hand-written arbitrary big-M bounds for these conditions would create unnecessary numerical and semantic risk.

## Decision

### Runtime and project tooling

Use:

- CPython `3.14.x`; initial development baseline `3.14.7`;
- one ordinary Python package using a `src/` layout, not a multi-package workspace;
- `uv` for environment/dependency resolution and a committed `uv.lock`; initial tooling baseline `uv 0.12.13`;
- `pyproject.toml` as the project/dependency configuration owner.

The four Bounded Contexts are modules inside this one Python package. They are not published/versioned as independent Python distributions.

### Relational persistence

Use file-backed SQLite for the first slice.

Required database settings/constraints:

- WAL journal mode;
- `read_uncommitted` remains disabled;
- foreign-key enforcement enabled for same-context relational invariants;
- one local filesystem database file; network/distributed filesystems are unsupported for this slice;
- planning snapshot capture uses one explicit read transaction/connection so all provider reads observe one SQLite snapshot;
- that read transaction ends before solver execution;
- integration tests use a temporary **file-backed** database, not `:memory:`, so WAL/snapshot behavior is actually exercised.

SQLite is an S4 implementation choice, not a new domain/architecture dependency. A later relational database can replace it without reopening S3 if the accepted module/data-ownership and consistent-read contracts remain intact.

### Persistence access and migrations

Use:

- SQLAlchemy Core `2.0.52`;
- Alembic `1.18.5`.

Use SQLAlchemy Core rather than the ORM in the first slice. Context-owned table definitions and explicit queries make cross-context persistence ownership visible and avoid accidental shared ORM entity graphs.

SQLite has no project-level schema namespaces, so table names use explicit context prefixes in the first slice:

- `nt_` — Nutrition Targeting;
- `fk_` — Food Knowledge;
- `mc_` — Market Catalog;
- `pp_` — Purchase Planning, if/when the authorized slice needs durable planning-owned state.

Cross-context database foreign keys are forbidden. A cross-context reference is an opaque provider identifier validated/used through the provider application contract, not relational ownership.

One Alembic migration stream deploys the monolith, but each migration/table change must state its owning context.

### Numeric persistence boundary

Authoritative decimal source values such as nutrient quantities and observed prices must not depend on SQLite binary floating-point storage for source fidelity.

For the first slice:

- persisted authoritative decimal values are stored in a canonical decimal textual representation and parsed to Python `Decimal` at the persistence boundary;
- currency remains an explicit code beside the amount;
- dates/timestamps use explicit ISO-8601 representations, with instants normalized to UTC;
- solver coefficients are derived as finite floating-point values only at the solver adapter boundary;
- reportable costs/coverage are recalculated from domain/application values after solving rather than copied from solver floating-point reports.

The exact reusable SQLAlchemy type helper is implementation detail; domain objects do not depend on SQLAlchemy.

### Optimization solver

Use:

- PySCIPOpt `6.2.1`;
- its compatible SCIP 10.x runtime provided by the official binary distribution; initial validated SCIP line `10.0.x`.

Reasons:

- mixed integer + continuous optimization matches package-count/planned-quantity semantics directly;
- SCIP supports native indicator and logical constraints, avoiding arbitrary hand-selected big-M bounds for conditional Purchase Group/variety logic where practical;
- the adapter can run in-process as required by S3;
- solver status exposes optimal/infeasible versus unfinished/error states;
- SCIP/PySCIPOpt are open-source and have Python 3.14 binary distributions for supported platforms.

Solver determinism configuration for the slice:

- single-threaded solving unless later evidence demonstrates a deterministic multi-thread configuration;
- fixed/default-zero randomization seeds recorded in the adapter configuration;
- stable variable/constraint construction order from immutable provider identifiers;
- sequential objective stages implement ADR-007; every stage must finish with proven optimality before the next stage/result is accepted;
- final technical tie resolution is applied only after all ADR-007 business stages.

A timeout or `unknown` with a feasible incumbent is a technical failure, not `partial`.

### Tests

Use pytest `9.1.1` as the test runner.

No web framework, API framework, ORM framework, task queue or message broker is introduced in the first slice.

The first external adapter is a small standard-library CLI used only to drive the end-to-end acceptance path. It must call application use cases and cannot bypass module boundaries.

## Consequences

- the slice can be run locally with one process and one database file;
- committed dependency locking makes the native solver/runtime environment reproducible;
- SQLAlchemy Core keeps persistence explicit and framework concerns outside domain policy;
- SQLite WAL can provide the S3 coherent-read snapshot without a database server;
- native SCIP indicator constraints reduce the need for brittle arbitrary big-M modeling;
- the stack is sufficient to validate the architecture but does not commit the product to an HTTP framework or long-term deployment platform.

## Alternatives considered

### PostgreSQL for the first slice

Deferred. PostgreSQL provides strong server-side concurrency and repeatable-read semantics, but a database server/container adds operational surface before there is a multi-user/deployment requirement. The persistence boundary remains relational so PostgreSQL can be adopted later without changing S3 ownership.

### SQLAlchemy ORM

Rejected for the first slice. It adds identity-map/entity relationship machinery that is not needed and makes accidental cross-context object graphs easier. Core is enough for explicit repositories/adapters.

### HiGHS/highspy

Not selected for the first slice. HiGHS is a capable open-source LP/MIP solver, but the current model benefits from native conditional/indicator modeling. SCIP exposes those constraints directly, reducing hand linearization and arbitrary bound selection.

### OR-Tools CP-SAT

Rejected for the current model because planned-utilized quantities are continuous domain decisions. Discretizing them to integer units solely to fit CP-SAT would change/approximate accepted semantics.

### Hand-written optimizer or enumeration

Rejected except as tiny test/reference logic. It would distract from product policy and would not scale to the accepted mixed-integer global basket problem.

### Add FastAPI/Pydantic immediately

Rejected for this slice. No accepted external API/UI behavior requires them. A CLI is sufficient to validate the complete application path while transport remains an outer adapter.

## Upgrade discipline

Exact resolved transitive versions belong to `uv.lock`. Direct dependency baselines above may be upgraded in ordinary implementation maintenance when tests prove compatibility and the upgrade does not alter accepted architecture/domain semantics. A solver or database change that invalidates S3 constraints must reopen S3.

## Supersession

Supersedes: none.
Superseded by: none.
