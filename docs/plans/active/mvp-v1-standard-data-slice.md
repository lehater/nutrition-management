# `mvp-v1` nutrition-standard data slice — readiness review

Status: `REWORK` — S2 applicability semantics must be reopened before implementation authorization.
Lifecycle owner: Nutrition Targeting / S2 Tactical Domain Design, then S4 Implementation Readiness.
Implementation authorization: **none**.

## Intended follow-up outcome

Make the accepted `mvp-v1` Nutrition Standard Set reproducibly loadable from sourced, versioned project data and establish explicit target-to-food mappings, without expanding into BLS food import, NIDDK/Hall execution, pediatric energy execution, UI/API work or a new optimization policy.

This is the first expected follow-up after the completed executable planning slice.

## What the first executable slice proved

PR #7 proved the architecture with a deliberately small `test-slice-v1` standard. Its `ReferenceDefinition`/persistence shape is not a claim that the complete DGE/ÖGE source can already be represented.

The production data slice must preserve the accepted source semantics in `docs/domain/nutrition-standard-set-mvp-v1.md` and `docs/domain/nutrient-semantics.md`; it must not flatten source rows merely to fit the test fixture model.

## Confirmed representation gaps

The current implementation cannot yet represent all accepted production semantics:

1. `ReferenceDefinition` has no age-band, sex or physiological-state applicability.
2. The current age model stores integer years; DGE contains sub-year infant bands, so source applicability needs exact calendar-band semantics.
3. `ReferenceBasis` lacks the accepted per-1000-kcal energy-density basis.
4. Source semantic kind (`recommended intake`, `estimated value`, `guideline`, etc.) is not persisted independently from downstream optimizer target shape.
5. Source unit, source identity/citation and row-level provenance are not represented in the persisted standard definition.
6. `PER_KG_DAILY` currently multiplies by current weight unconditionally, but accepted semantics require a source-owned applicable-weight rule.
7. Safety definitions do not yet encode source applicability/form scope required for reliable EFSA provenance and mapping.
8. The accepted target-to-food crosswalk is incomplete for a complete DGE/ÖGE corpus; missing mappings must remain explicit rather than being inferred by nutrient name.

These are implementation/data-model gaps, but source review also exposed unresolved product/domain applicability rules below.

## P1 domain blockers discovered from current DGE source

### P1 — adult zinc depends on phytate intake

DGE adult zinc recommendations are not a single age/sex value. They vary with low, medium or high phytate intake. The current MVP profile has no phytate-intake applicability fact, and choosing a default band would invent product policy.

Required S2 decision: either introduce an accepted applicability input/rule, or retain all source rows while reporting automated zinc-target selection as unsupported when the required factor is unavailable.

### P1 — adult female iron is not determined by age + sex alone

Current DGE iron recommendations distinguish pre-/postmenopausal and menstruating/non-menstruating situations in adult female rows. The MVP deliberately does not currently model such physiological state.

Required S2 decision: either introduce explicit profile/applicability facts, or retain the source rows while reporting automated iron-target selection as unsupported when the required factor is unavailable. Do not assume menstruation or menopause from age.

### P1 — protein body-weight basis is not simply current weight

DGE states that the g/kg protein values apply to normal weight and that, for adults with BMI >25 kg/m², normal weight should be used; the absolute g/day table is based on DGE reference weight. The current first-slice implementation always multiplies by current observed weight.

Required S2 decision: specify the `mvp-v1` applicable-weight rule for production protein derivation. Do not silently reuse the first-slice fixture behavior.

## Recommended KISS resolution direction

Do **not** add new sensitive/physiological profile fields merely to make every source row selectable in this slice.

Prefer a general source-applicability model that can store the complete sourced rows and can explicitly return `unsupported_applicability` when a row requires an input the MVP profile does not own. This follows the existing rule that source applicability must be exposed rather than guessed.

Under that direction:

- age/sex/general-state rows that are fully resolvable from current profile facts can be selected;
- pregnancy/lactation rows remain stored provenance but unselected, as already accepted;
- adult zinc and relevant iron rows remain sourced and queryable but are not automatically converted into a member target until an accepted applicability rule exists;
- no medium-phytate, menstruation or menopause default is invented;
- Purchase Planning continues to distinguish supported/mapped coverage from unsupported coverage.

This direction still requires an explicit S2 acceptance before implementation.

## Proposed implementation shape after S2 PASS

### Versioned source data

Use project-authored normalized data files under a versioned `data/nutrition/mvp-v1/` directory. Store numeric values as decimal strings and source identifiers/citations as data, not comments in Python code. Raw third-party publications/downloads are not vendored by default.

At minimum separate:

- standard/source manifest;
- nutrient reference rows;
- safety-limit rows;
- target-to-canonical-measure mappings;
- any project-defined derived-measure mapping metadata needed by Nutrition Targeting.

### Applicability representation

Represent source applicability independently from the resolved Member Nutrition Target. The representation must support:

- exact calendar age bands including months;
- sex-specific and sex-independent rows;
- general versus source-special physiological rows without implying those states are current MVP profile inputs;
- additional source applicability dimensions as explicit requirements rather than arbitrary columns/defaults.

A selector may only choose a row when every required applicability dimension is resolved by accepted profile/policy facts.

### Reference semantics

Persist enough information to reconstruct source meaning before downstream normalization:

- stable reference-row identity;
- nutrient/reference meaning;
- source semantic kind;
- source basis and unit;
- source value/bounds;
- applicability;
- source/version/citation provenance;
- accepted canonical target measure mapping and conversion/formula identity where applicable.

Extend the implemented basis set with the already accepted energy-density (`per 1000 kcal`) basis.

### Immutability and activation

`mvp-v1` remains immutable once used. Import is idempotent for identical data and fails on conflicting redefinition of an existing version. Only one standard version is active by default.

## Deliberate boundaries

Not part of this slice:

- BLS 4.0 food-row import;
- changing ADR-007 optimization policy;
- NIDDK/Hall weight-goal execution;
- enabling pediatric/infant energy execution;
- adding pregnancy/lactation targeting;
- introducing menstruation/menopause/phytate inputs unless separately accepted in S2;
- UI/API or synchronization workflows.

## Completion evidence after authorization

The implementation slice may be called complete only when:

- all S2 blockers above have accepted outcomes in canonical domain artifacts/ADR where consequential;
- a machine-readable `mvp-v1` source manifest and normalized reference dataset are committed with reproducible provenance;
- import from an empty migrated DB succeeds and repeated identical import is deterministic/idempotent;
- conflicting mutation of an already-used/versioned standard is rejected;
- exact calendar age-band boundaries and sex applicability are tested;
- source semantic kind/basis/unit/provenance round-trip losslessly;
- every automatically selected reference has an explicit accepted target mapping;
- unresolved applicability or unmapped semantics are surfaced explicitly and never silently defaulted;
- regression tests prove that the first executable slice still behaves identically for `test-slice-v1`;
- no source table or raw publication is bulk-copied into the repo without an explicit provenance/reuse decision.

## Next review action

Resolve the three P1 source-applicability questions in S2, then inventory the exact `mvp-v1` reference/mapping corpus and return to S4 readiness. Do not implement the production data import while these blockers remain.
