# Active execution

Current product work: make one bounded end-to-end implementation slice executable without widening accepted MVP scope.

Lifecycle stage: `S4 Implementation Readiness`.
Stage state: `IN_PROGRESS`.
Implementation authorization: `none` until S4 review passes.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS` for the accepted MVP scope.
- S3 Architecture: `PASS`; see [`../../architecture/target-architecture.md`](../../architecture/target-architecture.md), ADR-008 and ADR-009.

## Proposed first-slice stack

Accepted for readiness review by [`ADR-010`](../../decisions/ADR-010-first-implementation-stack.md):

- CPython 3.14.x, initial baseline 3.14.7;
- one `src/` Python package containing the four context modules;
- `uv` project/dependency management with committed `uv.lock`;
- file-backed SQLite in WAL mode for the first slice;
- SQLAlchemy Core 2.0.52 + Alembic 1.18.5;
- PySCIPOpt 6.2.1 / SCIP 10.x in-process solver adapter;
- pytest 9.1.1;
- standard-library CLI as the first outer adapter;
- no web/API framework, ORM, worker, queue or broker in this slice.

## Bounded implementation slice

Canonical scope: [`first-implementation-slice.md`](first-implementation-slice.md).

The authorized candidate slice crosses all four Bounded Contexts:

`current adult profiles + test-only standard fixture -> Household Nutrition Target -> Food/Market snapshot -> policy-optimal solver -> Purchase Plan JSON`.

The slice deliberately does not load/claim the full production `mvp-v1` DGE/ÖGE dataset or BLS catalog. Test fixture standards exist only to validate generic semantics and architecture.

## Readiness evidence defined before coding

The slice must produce:

- reproducible locked environment;
- schema migrations from an empty file DB;
- domain/unit tests;
- source/import-graph architecture-boundary tests;
- SQLite WAL coherent-read concurrency integration test;
- PySCIPOpt policy tests for package/planned quantities, market conditions, typed targets, variety, cost-close and technical tie ordering;
- explicit `mapped_complete`, `partial`, `no_executable_plan` and technical-failure evidence;
- deterministic repeated-plan acceptance test;
- end-to-end CLI/use-case test through all four contexts;
- performance characterization on acceptance-scale and larger synthetic catalogs.

## S4 review focus

Before `PASS`, verify:

1. the stack can realize every S3 invariant without framework leakage;
2. SQLite snapshot semantics are exercised with a real file/WAL rather than assumed from in-memory tests;
3. solver selection supports continuous + integer + conditional model semantics without hidden big-M approximations where native constraints are available;
4. sequential optimization can prove every ADR-007 stage before a plan is accepted;
5. first-slice exclusions are explicit and do not silently redefine accepted MVP behavior;
6. tests can detect cross-context persistence/import violations;
7. implementation can stop/reopen the correct upstream stage when runtime/numerical evidence invalidates S3 assumptions.

P0/P1 findings block implementation authorization.

## Current known verification risks

- **P2** — full technical lexicographic tie resolution may require multiple solver stages; measure it rather than replacing it with a hash/weighted approximation;
- **P2** — synchronous policy-optimal solve time on a larger plausible catalog is unknown until executable benchmarking;
- **P2** — SQLite is valid only for a local single-host file; a deployment requiring network/shared filesystem must select another relational database or revisit the deployment decision.

## Next

Complete S4 review of ADR-010 and the bounded slice. If no P0/P1 remains, mark S4 `PASS` and authorize **only** `first-implementation-slice.md`. Then implement it in a new branch/PR; any work outside that slice requires a new readiness decision.
