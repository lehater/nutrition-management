# Active execution

Current product work: implement the authorized sourced `mvp-v1` Nutrition Standard Set data/model/import slice.

Lifecycle state: **Implementation IN_PROGRESS** under accepted S2/S3/S4 gates.
Implementation authorization: **only** [`mvp-v1-standard-data-slice.md`](mvp-v1-standard-data-slice.md).

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; ADR-012 resolves source applicability and adult protein weight-basis semantics.
- S3 Architecture: `PASS`; existing modular monolith, Nutrition Targeting ownership and one relational store remain valid.
- S4 Implementation Readiness: `PASS` for this bounded standard-data/model/import slice.
- Planning/readiness increment: squash-merged as commit `1df17d8aa9181a8e8a8aa28b108b88f9e1ac2ec6` via PR #8.
- First executable implementation slice: completion gate `PASS`, squash-merged as commit `89e59831f9fd0fe83f9353ef498527f49e392342` via PR #7.

## Authorized implementation

Canonical scope: [`mvp-v1-standard-data-slice.md`](mvp-v1-standard-data-slice.md).

Implement:

`complete sourced mvp-v1 reference/safety corpus + complete explicit mapping-decision registry -> deterministic versioned import -> production adult target derivation with explicit unsupported coverage`.

The first implementation step is structural: extend the Nutrition Targeting domain/persistence and offline data-package validator so the source corpus can be represented without flattening applicability, units, provenance or mapping status. Only then load the production source values.

## Required completion evidence

Before this slice may be called complete:

- committed `data/nutrition/mvp-v1/` package validates offline;
- package/source digests are deterministic;
- migration works from the PR #7 schema and an empty database;
- import is transactional, identical-data idempotent and rejects conflicting same-version data;
- exactly one active default standard is preserved;
- every current DGE overview topic is accounted for and alcohol is explicitly non-active;
- exact age/sex/applicability boundaries, zinc/iron gaps and adult protein BMI/reference-weight boundaries are tested;
- `per_1000_kcal`, source kind/unit/basis/provenance and Safety Limit form scope round-trip losslessly;
- every active family has one explicit mapping decision and no mapping is inferred by display name;
- representative adult `mvp-v1` derivation carries resolved references and unsupported coverage correctly;
- `test-slice-v1` and architecture-boundary regression suites remain green.

## Guardrails

No BLS food-row import, NIDDK/Hall execution, pediatric/infant energy execution, pregnancy/lactation targeting, new phytate/menstruation/menopause profile inputs, optimizer-policy changes, UI/API or runtime scraping.

Open P0: `0`.
Open P1: `0` at implementation start.

Carried P2 risks remain documented in the readiness plan; none authorizes semantic fallback.

## Next

Implement the typed production Standard Set model, schema migration and deterministic offline data-package validator/import contract. Keep the implementation PR draft until the full sourced corpus and all completion evidence are green.
