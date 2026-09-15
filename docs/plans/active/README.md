# Active execution

Current product work: complete and merge the accepted first end-to-end executable planning slice.

Lifecycle basis: `S4 Implementation Readiness` authorization for the bounded first slice.
Implementation state: **completion gate PASS**.
Implementation authorization: only [`first-implementation-slice.md`](first-implementation-slice.md); no subsequent slice is authorized yet.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS` for the accepted MVP scope.
- S3 Architecture: `PASS`; see [`../../architecture/target-architecture.md`](../../architecture/target-architecture.md), ADR-008 and ADR-009.
- S4 Implementation Readiness: `PASS` for the bounded first slice; see ADR-010 and ADR-011.

## Completed first slice

Canonical scope: [`first-implementation-slice.md`](first-implementation-slice.md).

The implemented path crosses all four Bounded Contexts:

`two current adult profiles + test-only standard fixture -> Household Nutrition Target -> coherent Food/Market snapshot -> policy-optimal solver -> Purchase Plan JSON`.

The slice includes the locked CPython/uv environment, context-owned SQLite/Alembic persistence, coherent WAL read snapshots, the accepted adult target path, canonical Food Knowledge and executable Market Catalog projections, sequential ADR-007 optimization through PySCIPOpt/SCIP, canonical reporting, aggregate-only safety diagnostics and a standard-library CLI outer adapter.

Important boundary: `test-slice-v1` remains acceptance/test data only. The slice does not claim that the complete production `mvp-v1` DGE/ÖGE reference data or BLS catalog is implemented. NIDDK/Hall, pediatric/infant paths, HTTP/UI/authentication, saved plans/history, asynchronous planning and production deployment remain outside this slice.

ADR-011 separates `derivation_date` from timezone-aware `market_as_of`; both are retained in planning provenance. Market observations after `market_as_of` are not executable.

## Completion evidence

The completion gate is satisfied on GitHub Actions CI run `35016004825` (run #148) for commit `c6453c218d6a2ca273ca299b9a589fc1e13cf8e4`:

- locked environment and exact Python/library/SCIP version checks passed;
- migrations from an empty file-backed SQLite database passed;
- unit, policy, architecture-boundary, persistence/concurrency, deterministic E2E and CLI tests passed;
- solver-policy evidence covers package/planned quantities, target kinds, unknown evidence, variety, fulfilment costs, cost-close behavior, hard infeasibility and deterministic technical tie resolution;
- aggregate Safety Limit diagnostics remain non-guaranteeing and are tested, including known-lower-bound exceedance with unknown remaining contribution;
- performance characterization completed and uploaded as a CI artifact;
- every recorded sequential optimization stage in the final benchmark returned `optimal` and the final solver status was `policy_optimal`.

Historical performance evidence is recorded in [`../../baseline/first-implementation-slice-performance.md`](../../baseline/first-implementation-slice-performance.md).

## Review result

Final implementation review found no remaining **P0/P1** issue for the bounded slice.

Resolved during implementation/review included:

- explicit non-legacy SQLite transaction control for coherent WAL read snapshots;
- version-safe Nutrition Standard Set persistence and single active-version behavior;
- PAL activity-adjustment provenance and applicability checks;
- distinct nutrition derivation date and market evaluation instant;
- future-observation exclusion and timezone-aware Market Catalog timestamps;
- explicit commercial-value/domain invariants;
- lower-bound unknown-evidence semantics;
- solver/reporter mechanical tolerance separation from business thresholds;
- safety diagnostics that never claim member-allocation safety.

## Remaining non-blocking risks

- **P2** — solver scalability: exact technical lexicographic tie resolution adds sequential stages per Offer. Final baseline: 16 Offers = 45 stages / 14.785100 s; 32 Offers = 77 stages / 50.462863 s on the recorded GitHub runner. Re-characterize before materially increasing catalog size or setting latency expectations.
- **P2** — floating-point solver mechanics remain intentionally isolated from domain thresholds; keep canonical Decimal revalidation and regression tests when changing solver code.
- **P2** — SQLite remains a first-slice local/single-host choice; network/shared-filesystem deployment is unsupported.

None of these P2 risks justifies changing accepted business semantics inside this slice.

## Next

Squash-merge PR #7. The last executable/schema change is commit `c6453c218d6a2ca273ca299b9a589fc1e13cf8e4`, which passed the full completion CI; commits after it only record completion evidence and execution state. After merge, open a fresh planning increment from `main` and choose the next bounded slice explicitly; do not implicitly expand this implementation authorization.
