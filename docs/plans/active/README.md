# Active execution

Current product work: define and unblock the next bounded slice for sourced `mvp-v1` Nutrition Standard Set data and target mappings.

Lifecycle state: **S2 REOPEN / REWORK** for source applicability semantics discovered during follow-up planning.
Implementation authorization: **none** for the next slice.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: previously `PASS`; narrowly reopened for production nutrition-reference applicability.
- S3 Architecture: `PASS` for the existing modular-monolith/planning architecture; no architecture reopen is currently required.
- First implementation slice: completion gate `PASS`, squash-merged as commit `89e59831f9fd0fe83f9353ef498527f49e392342` via PR #7.

Historical performance evidence for that slice remains in [`../../baseline/first-implementation-slice-performance.md`](../../baseline/first-implementation-slice-performance.md).

## Current candidate slice

Readiness document: [`mvp-v1-standard-data-slice.md`](mvp-v1-standard-data-slice.md).

Intended outcome:

`complete sourced mvp-v1 reference rows + explicit target mappings -> reproducible versioned import`

without BLS food-row import, NIDDK/Hall execution, pediatric energy execution, UI/API or optimization-policy changes.

## Why S2 is reopened

Reviewing the current DGE source against the accepted model exposed source applicability that cannot be selected from the current MVP profile without inventing defaults:

- **P1** — adult zinc recommendations vary by phytate intake;
- **P1** — adult female iron recommendations vary by menstruation/menopausal state, not age + sex alone;
- **P1** — protein g/kg production derivation requires an explicit applicable-weight rule and cannot universally use current observed weight.

The first executable slice remains valid because it used the deliberately synthetic `test-slice-v1` standard and made no production `mvp-v1` claim.

## Recommended direction under review

Prefer storing complete source applicability while returning explicit `unsupported_applicability` when a required source factor is not owned by the MVP profile. Do not add sensitive profile fields or invent medium-phytate/menstruation/menopause defaults merely to force automatic selection.

This direction must be accepted in canonical S2 artifacts before implementation.

## Additional implementation-readiness gaps after S2 resolution

The current production-standard model must still be extended to preserve:

- exact calendar age bands including sub-year groups;
- sex/general-state applicability;
- per-1000-kcal energy-density basis;
- source semantic kind independently from downstream optimizer shape;
- source unit and row-level source/version/citation provenance;
- source-owned body-weight basis rules;
- safety applicability/form scope;
- complete explicit target-to-canonical-measure crosswalk coverage.

These are not permission to implement yet; they are the expected S4 work once the P1 domain blockers are closed.

## Non-blocking carried risks

- **P2** — exact solver technical tie-resolution scales poorly; re-characterize before materially increasing executable catalog size.
- **P2** — keep floating-point solver tolerances isolated from domain thresholds.
- **P2** — SQLite remains local/single-host only.

## Next

Resolve the three P1 applicability decisions in S2. Then inventory the exact `mvp-v1` reference/mapping corpus and run S4 readiness for the data/import slice. Do not start production standard import until that gate passes.
