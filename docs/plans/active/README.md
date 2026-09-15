# Active execution

Current product work: implement the accepted first end-to-end executable planning slice.

Lifecycle stage: `S4 Implementation Readiness`.
Stage state: `PASS` for the bounded first slice.
Implementation authorization: **only** [`first-implementation-slice.md`](first-implementation-slice.md).

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS` for the accepted MVP scope.
- S3 Architecture: `PASS`; see [`../../architecture/target-architecture.md`](../../architecture/target-architecture.md), ADR-008 and ADR-009.

## Accepted first-slice stack

[`ADR-010`](../../decisions/ADR-010-first-implementation-stack.md) fixes the implementation baseline for this slice:

- CPython 3.14.x, initial baseline 3.14.7;
- one `src/` Python package containing the four context modules;
- `uv` dependency/project management with committed `uv.lock`;
- file-backed SQLite on a local filesystem with WAL, `synchronous=FULL`, foreign keys enabled and `read_uncommitted` disabled;
- SQLAlchemy Core 2.0.52 + Alembic 1.18.5;
- PySCIPOpt 6.2.1 / compatible SCIP 10.x in-process solver adapter;
- pytest 9.1.1;
- standard-library CLI as the first outer adapter;
- no web/API framework, ORM, worker, queue or broker in this slice.

## Authorized implementation scope

Canonical scope: [`first-implementation-slice.md`](first-implementation-slice.md).

The slice crosses all four Bounded Contexts:

`two current adult profiles + test-only standard fixture -> Household Nutrition Target -> coherent Food/Market snapshot -> policy-optimal solver -> Purchase Plan JSON`.

Important boundary: `test-slice-v1` is acceptance/test data only. The slice does not claim that the complete product `mvp-v1` DGE/ÖGE reference data or BLS catalog is implemented.

The adult path must also enforce accepted profile applicability, including date-of-birth age resolution, valid resolved PAL semantics and `current_weight_date <= derivation_date`; unsupported weight-goal/pediatric paths fail explicitly rather than falling back silently.

## S4 review result

No remaining P0/P1 implementation-readiness issue is known for the bounded slice.

Readiness review confirms:

- SQLite WAL can realize the S3 one-run coherent read snapshot when provider reads share one explicit connection/read transaction; acceptance tests must use a real file-backed DB;
- SQLAlchemy Core preserves explicit context-owned persistence without requiring shared ORM entities;
- PySCIPOpt/SCIP supports the mixed integer + continuous model and native indicator/logical constraints needed to avoid arbitrary hand-written big-M values where practical;
- the solver adapter must prove every ADR-007 sequential stage before a plan is returned;
- a feasible timeout/unknown incumbent remains a technical failure, never `partial`;
- the final technical order is implemented exactly after business objectives, not replaced by hash/weighted approximations;
- implementation capability gaps remain explicit and cannot redefine accepted S1/S2 behavior.

## Required completion evidence

Before this implementation slice may be called complete, it must provide:

- reproducible locked environment and exact runtime/solver version evidence;
- migrations from an empty local SQLite database;
- unit tests for the implemented adult target/profile path and accepted planning policy;
- import/dependency architecture-boundary tests;
- file-backed WAL coherent-read concurrency test;
- solver-policy fixtures for package/planned quantities, target kinds, unknown data, variety, fulfilment costs, cost-close, hard infeasibility and technical tie resolution;
- deterministic repeated-plan acceptance test;
- end-to-end CLI/use-case test through all four contexts;
- performance characterization with problem size, solver stage statuses and wall-clock timing.

## Non-blocking implementation risks

- **P2** — exact technical lexicographic tie resolution may add many sequential solve stages as candidate count grows; measure before attempting optimization shortcuts;
- **P2** — synchronous policy-optimal solve time for a plausible larger catalog remains unmeasured;
- **P2** — floating-point solver tolerances must be shown not to mutate ADR-007/domain tolerance semantics; reportable facts are recalculated outside solver reporting;
- **P2** — SQLite is a first-slice local/single-host choice; network/shared-filesystem deployment is unsupported.

If these produce evidence that the accepted architecture cannot work, stop and reopen S3. Do not add background workers, approximate objectives or semantic fallbacks inside the implementation PR.

## Explicitly not authorized yet

- complete production `mvp-v1` standards/reference import;
- complete BLS 4.0 catalog import;
- NIDDK/Hall weight-goal path;
- pediatric/infant derivation paths;
- HTTP/UI/authentication;
- saved plans/history;
- asynchronous planning;
- production hosting/deployment work.

## Next

Create a fresh implementation branch from `main` after this readiness PR is squash-merged. Implement only `first-implementation-slice.md`, run/record the required evidence, review findings by P0/P1/P2/P3, and merge only when the slice completion gate passes.
