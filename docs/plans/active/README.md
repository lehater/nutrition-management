# Active execution

Current product work: prepare and authorize the bounded BLS 4.0 Food Knowledge source-data/import slice.

Lifecycle state: **S4 Implementation Readiness PASS** under accepted S0–S3 product semantics and architecture.
Implementation authorization after this planning PR merges: **only** [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md).

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; ADR-004 makes BLS 4.0 the canonical MVP food-composition vocabulary and ADR-005 owns the project food-category taxonomy.
- S3 Architecture: `PASS`; existing modular monolith, Food Knowledge ownership and one relational store remain valid.
- Previous `mvp-v1` Nutrition Standard Set slice: completion gate `PASS`, squash-merged as commit `93b44914913ec9b8bdfdfd69d9bd48cc2fefaf4a` via PR #9.

## Selected next slice

Canonical readiness plan: [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md).

Authorized outcome after merge:

`official pinned BLS 4.0 XLSX inputs -> deterministic normalized Food Knowledge package -> transactional/idempotent production import -> BLS-backed Base Food facts available through existing planning boundary`.

The implementation preserves:

- BLS 4.0 component codes/native units and `100 g edible portion` basis;
- all 138 component definitions;
- missing / trace / zero / known distinctions;
- per-value origin/reference provenance;
- deterministic BLS-code-scoped Base Food identity;
- explicit project-owned category mapping with exact-one classification coverage.

## Readiness evidence

Official MRI BLS 4.0 source boundary is concrete:

- source package version: BLS `4.0`, publication year `2025`;
- DOI: `10.25826/Data20251217-134202-0`;
- license: `CC BY 4.0` with Max Rubner-Institut attribution;
- documented main workbook: `BLS_4_0_Daten_2025_DE.xlsx` with 7,140 foods and 138 nutrient components;
- documented component workbook: `BLS_4_0_Components_DE_EN.xlsx`;
- each nutrient cell carries value, data-origin category and reference fields;
- all source quantities use the already accepted `100 g edible portion` basis.

S4 P0: `0`.
S4 P1: `0`.

Carried P2 implementation risks are recorded in the slice plan and do not authorize heuristic category/name mapping, runtime scraping or semantic fallback.

## Guardrails

This slice does not authorize:

- Market Catalog price/product acquisition or automatic SKU-to-BLS matching;
- optimizer-policy changes;
- new Nutrition Targeting mappings;
- NIDDK/Hall execution;
- pediatric/infant execution;
- UI/API/authentication;
- runtime BLS synchronization;
- saved Purchase Plan history.

## Next

Squash-merge this planning/readiness PR. Use the resulting `main` SHA as the base of a fresh implementation branch and implement only the BLS 4.0 source normalization, deterministic package, Food Knowledge persistence/import and regression work authorized by the active plan.