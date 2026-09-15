# `mvp-v1` nutrition-standard data slice — implementation readiness

Status: `PASS` — S2 applicability reopen and bounded S4 readiness are complete.
Lifecycle owner: Nutrition Targeting / S2 Tactical Domain Design + S4 Implementation Readiness.
Implementation authorization: **only the bounded slice defined in this file** after this planning PR is merged.

## Outcome

Make the accepted `mvp-v1` Nutrition Standard Set reproducibly loadable from committed, sourced, versioned project data and provide a complete registry of target-to-food mapping decisions.

“Complete mapping registry” means every active reference family has an explicit decision: `mapped` to an accepted ADR-004 Nutrient Measure or `unsupported` with a reason. It does **not** authorize name-based or chemically broader mappings merely to maximize coverage.

This slice does not import BLS food rows and does not expand product profile scope.

## S2 reopen result

The three source-applicability P1 blockers are resolved by [`ADR-012`](../../decisions/ADR-012-source-applicability-and-protein-weight-basis.md).

Accepted semantics:

- the Standard Set stores stable reference families plus source variant rows;
- selection requires every applicability dimension needed for one unique active row;
- missing MVP-owned applicability facts produce `unsupported_applicability`, never a guessed default;
- known facts outside a general source reference produce `source_inapplicable`;
- pregnancy/lactation rows remain sourced `outside_mvp_scope` provenance;
- adult zinc requiring phytate class is unsupported for automatic selection under the current profile;
- affected female iron families requiring menstruation/menopause state are unsupported for automatic selection under the current profile;
- adult DGE protein uses current weight for `18.5 <= BMI < 25.0`, BMI-22 reference weight for `25.0 <= BMI < 30.0`, and is `source_inapplicable` for automatic general-reference derivation at BMI `<18.5` or `>=30.0`.

No new phytate, menstruation or menopause profile fields are introduced.

S2 gate: **PASS**. No unresolved P0/P1 domain contradiction is known for this slice.

## Source corpus boundary

### DGE/ÖGE adequacy/reference corpus

The committed source manifest must account for every topic in the current DGE reference-value overview:

- energy;
- protein;
- fat / essential fatty acids;
- carbohydrates;
- fibre;
- alcohol;
- water;
- vitamins A, D, E, K, thiamin, riboflavin, niacin, B6, folate, pantothenic acid, biotin, B12 and C;
- sodium, chloride, potassium, calcium, phosphorus and magnesium;
- iron, iodine, fluoride, zinc, selenium, copper, chromium, manganese and molybdenum.

“Account for” means a topic is represented by sourced active reference families/rows, by an accepted derivation policy, or by an explicit non-active status. In particular, the DGE alcohol page states that the 2024 DGE position paper replaced the former alcohol reference value; the data set must not resurrect a legacy numeric alcohol target.

The manifest pins DGE/ÖGE 3rd edition, 1st issue 2025 plus the May 2026 erratum and records the concrete official page/source used for each family.

### EFSA safety corpus

For EFSA UL overview version 11 (August 2025), include every UL/safe-level row relevant to substances represented by the DGE/ÖGE reference corpus, retaining population applicability and exact substance/form scope even when Food Knowledge cannot map it quantitatively.

Safety limits remain separate from preferred Nutrient References and from optimizer target maxima.

## Canonical project data package

Use JSON only; do not add a YAML/parser dependency.

Canonical files live under:

`data/nutrition/mvp-v1/`

Required files:

- `manifest.json` — standard version, source documents/pages, edition/correction metadata, file inventory and SHA-256 content digests;
- `references.json` — reference families and sourced variant rows;
- `safety_limits.json` — sourced Safety Limit families/rows and substance/form scope;
- `mappings.json` — one explicit mapping decision per active reference family plus safety mapping decisions where applicable.

Numeric source values are decimal strings. Source text/labels needed for provenance are stored as short metadata; raw third-party publications/pages are not vendored by default.

The importer reads only these committed normalized files. Production behavior does not scrape DGE/EFSA/BLS websites at runtime.

## Reference representation

A production reference row must preserve at least:

- `family_id` — stable nutrient-reference family identity;
- `row_id` — stable source variant identity unique inside one Standard Set;
- nutrient/reference meaning;
- source semantic kind (`recommended_intake`, `estimated_value`, `guideline`, etc.);
- downstream target shape (`adequacy_floor`, `lower_bound`, `upper_bound`, `interval`, `point`);
- native basis (`absolute_daily`, `per_kg_daily`, `percent_energy`, `per_1000_kcal`);
- native source unit;
- source value/bounds and energy factor where applicable;
- source applicability;
- applicable-weight rule identity where applicable;
- source document/page identity and row/footnote locator;
- source scope (`active`, `outside_mvp_scope`, or another explicit non-active reason).

Reference-family identity, source-row identity and food-side mapping identity are separate concepts.

## Applicability representation

Applicability belongs to source rows, not to the resolved Member Nutrition Target.

Age bounds preserve source units rather than converting all ages to approximate days. Represent age boundaries as explicit `{value, unit}` values where unit is `months` or `years`, with inclusive lower and exclusive upper bounds where supplied.

Selection rules:

- year-based bands use the already accepted chronological-age-in-years semantics;
- sub-year month bands use completed calendar months;
- for a monthly anniversary whose original day does not exist in the target month, that month's last calendar day is the anniversary;
- the 4–<12-month / 1-year transition is represented with the source's one-year boundary, not a synthetic fixed-day duration;
- sex-independent and sex-specific rows are explicit;
- additional applicability requirements are represented as typed dimension/value predicates rather than hidden defaults;
- source-special rows may be retained as `outside_mvp_scope` without creating new profile inputs.

If fully resolved facts match more than one active row in a family, the Standard Set is invalid and import/validation fails.

## Mapping registry

`mappings.json` is a complete decision registry, not a name matcher.

For each active reference family it records one of:

- `mapped` — accepted canonical Food Knowledge component/derived measure, canonical unit and formula identity if needed;
- `unsupported` — explicit reason such as no BLS 4.0 component, chemical/form mismatch, missing accepted conversion, or upstream source semantics not comparable to food composition.

Only mappings already accepted by ADR-004 / `docs/domain/nutrient-semantics.md` may be marked `mapped` in this slice. An apparently obvious new mapping discovered during import must stop at S2 review rather than being inferred in code/data.

The official BLS 4.0 component vocabulary is validation evidence only in this slice; BLS food rows are not imported.

## Persistence/model migration

Keep the accepted modular-monolith/one-database architecture. No S3 reopen is needed.

Extend Nutrition Targeting persistence rather than introducing a second standards store:

- `nt_standard_set` gains immutable content/source digest metadata;
- `nt_standard_reference` keeps `(standard_version, row_id/reference_id)` identity and gains family identity, source semantic kind/unit, source scope, applicability, source provenance and applicable-weight metadata;
- add a context-owned target-mapping table keyed by `(standard_version, family_id)`; canonical Food Knowledge measure IDs remain scalar cross-context references with no SQL FK;
- extend Safety Limit persistence with applicability, semantic kind, exact substance/form scope and source provenance;
- `ReferenceBasis` gains the already accepted `per_1000_kcal` basis;
- existing `test-slice-v1` remains representable and its current behavior is regression-protected.

Applicability may be stored as canonical JSON text inside Nutrition Targeting persistence because selection is context-owned and no SQL query across applicability dimensions is required. Domain objects remain typed and validate the decoded representation.

## Import and immutability

The data package has one deterministic SHA-256 content digest derived from the canonical file bytes listed by `manifest.json`.

Import rules:

1. validate file/schema/referential integrity before writes;
2. validate family/row uniqueness, applicability determinism where facts are fully specified, mapping registry completeness and source references;
3. if the version does not exist, insert it transactionally;
4. if the same version exists with the same digest, import is an idempotent no-op;
5. if the same version exists with a different digest, fail as conflicting immutable redefinition;
6. activation is explicit and atomically deactivates the previous default version;
7. malformed or incomplete source data never partially activates.

No runtime network call is part of import or target derivation.

## Target contract changes

Production `MemberNutritionTarget` / `HouseholdNutritionTarget` gain explicit applicability-gap provenance required by ADR-012.

For currently implemented adult derivation:

- `mvp-v1` resolved adult families are quantitatively derived using source basis/unit rules;
- adult zinc and affected female iron remain `unsupported_applicability` without profile expansion;
- adult protein applies the ADR-012 weight rule;
- unresolved mappings remain unsupported coverage;
- unsupported coverage reaches Purchase Plan reporting without entering numeric solver objectives.

Pediatric/infant source rows may be stored and validated, but this slice does not authorize their energy-derivation execution path.

## Deliberate boundaries

Not authorized:

- BLS 4.0 food-row import;
- changing ADR-007 optimization policy;
- NIDDK/Hall weight-goal execution;
- enabling pediatric/infant energy execution;
- pregnancy/lactation targeting;
- new phytate/menstruation/menopause profile inputs;
- UI/API;
- network synchronization/scraping;
- approximate/name-based nutrient mapping.

## Required tests/evidence

Before the implementation slice is complete:

- committed `mvp-v1` files validate from an empty checkout without network access;
- manifest digests and row/source references are deterministic;
- migration works from the PR #7 schema and from an empty database;
- identical import is idempotent and conflicting same-version data is rejected;
- activation preserves exactly one active default version;
- every DGE overview topic is accounted for in the manifest and alcohol is explicitly non-active rather than given a legacy target;
- exact year/month age boundaries are tested, including an end-of-month infant DOB case;
- sex applicability, zinc phytate gaps and female iron applicability gaps are tested;
- adult protein normal/overweight/underweight/obesity boundaries are tested at BMI `18.5`, `25.0` and `30.0`;
- `per_1000_kcal` reference derivation is tested;
- source semantic kind, unit, basis, applicability and provenance round-trip losslessly;
- every active family has exactly one mapping-registry decision;
- mapped entries correspond to accepted ADR-004 semantics; unsupported entries remain visible;
- Safety Limit substance/form scope is retained and unmappable limits never become hard constraints;
- representative adult `mvp-v1` Member/Household target derivation proves resolved references plus unsupported applicability/mapping propagation;
- the full PR #7 test suite for `test-slice-v1` remains green;
- architecture-boundary tests remain green.

## Readiness review

S3 remains valid: all new semantics and persistence are internal to Nutrition Targeting and use the existing published target boundary. No distributed component, new database or cross-context persistence dependency is needed.

S4 P0: `0`.
S4 P1: `0`.

Non-blocking risks:

- **P2** — manual normalized-source transcription can introduce row errors; mitigate with row-level citations, deterministic validation and sentinel review tests, not runtime scraping;
- **P2** — some DGE families will remain unsupported quantitatively because ADR-004 has no accepted food-side mapping; this is expected unsupported coverage, not permission to infer mappings;
- **P2** — EFSA safety form scope may leave many diagnostics unmappable; retain the source semantics rather than broadening them.

Implementation readiness: **PASS** for this bounded slice.

## Next

Merge this planning/domain-readiness increment, then create a fresh implementation branch from `main`. Implement only the data/model/import/target-contract work authorized here; do not combine the BLS food-data import into the same PR.
