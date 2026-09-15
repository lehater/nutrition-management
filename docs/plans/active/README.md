# Active execution

Current product work: finalize and merge the planning/readiness increment for sourced `mvp-v1` Nutrition Standard Set data and target-mapping decisions.

Lifecycle state: **S2 PASS / S4 PASS** for the bounded `mvp-v1` standard-data slice.
Implementation authorization: **only** [`mvp-v1-standard-data-slice.md`](mvp-v1-standard-data-slice.md), after this planning PR is merged and implementation starts from a fresh branch.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; the narrow source-applicability reopen is resolved by ADR-012.
- S3 Architecture: `PASS`; the existing modular monolith, Nutrition Targeting ownership and one relational store remain valid.
- S4 Implementation Readiness: `PASS` for the bounded standard-data/model/import slice.
- First implementation slice: completion gate `PASS`, squash-merged as commit `89e59831f9fd0fe83f9353ef498527f49e392342` via PR #7.

Historical performance evidence for the first slice remains in [`../../baseline/first-implementation-slice-performance.md`](../../baseline/first-implementation-slice-performance.md).

## Authorized next slice

Canonical readiness document: [`mvp-v1-standard-data-slice.md`](mvp-v1-standard-data-slice.md).

Outcome:

`complete sourced mvp-v1 reference/safety corpus + complete explicit mapping-decision registry -> deterministic versioned import -> production adult target derivation with explicit unsupported coverage`

The mapping registry is complete when every active reference family has either an accepted ADR-004 mapping or an explicit unsupported reason. Completeness does not mean forcing every DGE concept onto a similarly named BLS component.

## S2 reopen resolution

ADR-012 resolves the three former P1 blockers:

- adult zinc source variants depend on phytate class; the current MVP profile does not own that fact, so automatic adult zinc resolution is `unsupported_applicability` rather than a medium-phytate default;
- affected female iron source variants depend on menstruation/menopausal applicability; the MVP does not infer those states from age, so unresolved families remain `unsupported_applicability`;
- adult DGE protein uses current observed weight for normal BMI, BMI-22 reference weight for overweight BMI, and becomes `source_inapplicable` for the general automatic rule at BMI `<18.5` or `>=30.0`.

Member and Household Nutrition Targets preserve those active applicability gaps. Purchase Planning reports them as unsupported coverage and does not invent numeric objectives.

No new phytate, menstruation or menopause profile fields are added.

## S4 implementation shape

The authorized implementation uses committed JSON under `data/nutrition/mvp-v1/`, with a source/digest manifest, reference rows, safety rows and mapping decisions. It extends the existing Nutrition Targeting model/persistence rather than adding another standards store or service.

The source manifest accounts for every current DGE reference-overview topic. Alcohol is explicitly non-active because the DGE states that its 2024 position paper replaced the former alcohol reference value; legacy alcohol limits must not reappear as an `mvp-v1` nutrient target.

The model adds stable reference-family identity, source-row applicability, source semantic kind/unit/provenance, the accepted per-1000-kcal basis, source-owned applicable-weight metadata, Safety Limit form scope and an explicit mapping registry. Cross-context canonical measure IDs remain scalar references with no SQL foreign key.

Import is offline, transactional and immutable by version/content digest: identical data is idempotent; a conflicting same-version redefinition fails.

## Gate review

Open P0: `0`.
Open P1: `0`.

Known P2 risks:

- normalized source transcription can contain human errors; mitigate with row citations, deterministic validators and sentinel review tests;
- some reference/safety families remain quantitatively unsupported because no accepted ADR-004 food-side mapping exists;
- solver scalability, numeric-tolerance isolation and SQLite local/single-host constraints from the first slice remain carried risks but are not changed by this data slice.

No P2 authorizes semantic fallback or name-based mapping.

## Explicitly not authorized

- BLS 4.0 food-row import;
- NIDDK/Hall execution;
- pediatric/infant energy execution;
- pregnancy/lactation targeting;
- new sensitive applicability profile inputs;
- optimizer-policy changes;
- UI/API;
- network scraping/synchronization.

## Next

Complete final PR #8 review, squash-merge this planning/domain-readiness increment, then create a fresh implementation branch from `main` and implement only the authorized `mvp-v1` standard-data slice.
