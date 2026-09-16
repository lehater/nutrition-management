# BLS 4.0 Food Knowledge import slice — implementation readiness

Status: `PASS` — bounded S4 implementation readiness.
Lifecycle owner: Food Knowledge / S4 Implementation Readiness.
Implementation authorization: **only the bounded slice defined in this file** after this planning PR is merged.

## Outcome

Make the official BLS 4.0 data set reproducibly importable into Food Knowledge as the production baseline theoretical food catalog while preserving the canonical component semantics already accepted by ADR-004 and the project food-category semantics accepted by ADR-005.

The slice turns the current fixture/manual `FoodFact` path into a production-capable BLS path without changing Purchase Planning policy, Nutrition Targeting policy, Market Catalog acquisition, UI/API or runtime network behavior.

## Accepted upstream semantics

No S2 or S3 reopen is required.

- ADR-004 already makes BLS 4.0 component codes and native units the MVP canonical food-composition vocabulary and fixes the canonical basis at `100 g edible portion`.
- Food Knowledge already owns Base Food identity, nutrient profile, source provenance and top-level category classification.
- ADR-005 already defines the controlled eight-category project taxonomy and rejects using BLS groups directly as the planning taxonomy.
- The modular-monolith / one-database architecture remains valid; the new persistence is internal to Food Knowledge.

The implementation must stop for S2 review if source inspection reveals a semantic case that cannot be represented without weakening these accepted meanings.

## Official source boundary

Pin BLS 4.0 from the Max Rubner-Institut (MRI):

- dataset: `Bundeslebensmittelschlüssel (BLS), Version 4.0 — Deutsche Nährstoffdatenbank`;
- publisher: Max Rubner-Institut;
- publication/version year: `2025`, BLS version `4.0`;
- DOI: `10.25826/Data20251217-134202-0`;
- license: `CC BY 4.0` with MRI attribution;
- official download page: `https://www.blsdb.de/download`;
- official documentation/FAQ: `https://www.blsdb.de/bls` and `https://www.blsdb.de/faq`.

The documented source package contains at least:

- `BLS_4_0_Daten_2025_DE.xlsx` — 7,140 food rows; first three columns are BLS code, German name and English name; then three columns per each of 138 components: nutrient value, value origin and reference;
- `BLS_4_0_Components_DE_EN.xlsx` — component code, German/English name, native unit, component group and documented formula metadata.

All source nutrient quantities are already expressed per `100 g edible portion`.

Raw BLS files are build/import inputs, not runtime dependencies. Production planning and normal application startup must make no network request to BLS/OpenAgrar/GovData.

## Source pinning and reproducibility

The implementation must record a source manifest containing:

- BLS version and DOI;
- exact input filenames;
- official source/download URLs used to obtain them;
- SHA-256 digest of each exact input file;
- license and required attribution;
- normalization/package format version.

An input whose digest does not match the pinned source manifest is rejected. A rotating/tokenized web download URL is not an identity boundary; DOI + version + exact file digest are.

Do not silently accept a later BLS 4.x release under the `4.0` identity.

## Canonical normalized package

Commit a deterministic normalized package under:

`data/food/bls-4.0/`

The committed package is the production import input. The official XLSX files do not need to be vendored when the normalized package contains complete source identity/digests and can be reproduced by the repository build tool from the pinned official inputs.

Use deterministic JSON shards rather than one monolithic document. Missing component cells may be omitted because the component catalog defines the complete vocabulary and absence is canonically `missing`. Explicit zero and trace observations must remain explicit records.

Minimum package contents:

- `manifest.json` — package format/version, source identity/digests, generated-file inventory/digests, counts and attribution;
- `components.json` — all 138 BLS component definitions needed to validate code/unit semantics;
- `category_mappings.json` — project-owned BLS-code classification decisions;
- deterministic food shards ordered by BLS code, containing Base Food identity/name/category plus non-missing nutrient evidence and per-value provenance.

The package digest is derived deterministically from canonical generated content and file inventory. Generation from the same source inputs and mapping registry must reproduce byte-identical output.

## Base Food identity

Use deterministic source-scoped IDs:

`bls:4.0:<BLS_CODE>`

Retain the original BLS code separately as source identity/provenance. Do not use German/English display names as identity.

Existing test/manual Base Food IDs remain valid and are not rewritten.

## Component semantics

Import all 138 BLS 4.0 component definitions. At minimum retain:

- component code;
- German and English names;
- native unit;
- German/English component group where present;
- documented formula and formula-application metadata where present;
- source vocabulary version `BLS 4.0`.

A food nutrient record references a canonical component code. The importer must reject unknown component codes, duplicate component definitions or unit disagreement with the pinned BLS component catalog.

This slice does not invent new Nutrition Targeting mappings. Only mappings already accepted in the active Nutrition Standard Set become quantitatively comparable to imported BLS values.

## Nutrient evidence and provenance

For every source food/component cell preserve the current domain distinction:

- source cell absent -> `missing` and no persisted nutrient value row is required;
- source value-origin `Spuren` / trace -> `trace`, no quantitative amount used for deterministic coverage;
- numeric zero with a non-trace origin -> `zero` with amount `0`;
- positive numeric value -> `known` with the exact decimal text converted losslessly to `Decimal` semantics.

For every explicit non-missing nutrient record retain at least:

- canonical component code;
- normalized status;
- normalized amount when quantitative;
- original source value text needed to audit source precision;
- BLS value-origin category;
- source reference text when supplied;
- source/version identity.

`Logische Null` remains zero with that provenance. Trace must not become zero even when the workbook displays a numeric-looking zero. A missing cell must never become zero.

The parser rejects negative nutrient quantities and structurally inconsistent source cells rather than guessing repair rules.

## Food category classification

ADR-005 project categories remain authoritative; BLS food groups are source classification evidence only.

`category_mappings.json` is an explicit versioned decision registry over BLS codes/code prefixes. It may contain narrow prefix rules plus exact-code overrides, but generation must prove that every imported BLS food code resolves to **exactly one** project top-level category.

Rules:

- no display-name keyword classification;
- no store/merchant taxonomy inference;
- no implicit catch-all fallback;
- `other_or_composite` must be an explicit mapping decision, not an error sink;
- overlapping mapping rules that produce ambiguity are rejected;
- an unmapped source food rejects production package generation.

This registry is project-owned Food Knowledge data and is reviewed independently of MRI source truth.

## Persistence and import

Extend Food Knowledge persistence in place; do not create another database or cross-context FK.

The implementation may add context-owned persistence for:

- BLS component definitions;
- source-dataset digest/version metadata;
- Base Food source code / English name where needed;
- per-nutrient value origin, reference and raw source value text.

Existing `fk_base_food` / `fk_nutrient_value` concepts remain the storage boundary. Cross-context consumers continue to receive published Food Knowledge facts rather than persistence objects.

Import requirements:

1. validate package manifest/file digests before writes;
2. validate component vocabulary, food identity, category exact-one coverage and nutrient evidence semantics before writes;
3. import transactionally;
4. identical BLS 4.0 package import is idempotent;
5. same source-version identity with a different package/source digest is rejected as conflicting redefinition;
6. a failed import leaves existing Food Knowledge data unchanged;
7. test/manual food fixtures remain representable for regression tests.

This slice does not define automatic BLS version upgrade/activation policy beyond the pinned 4.0 baseline.

## Build tooling boundary

A repository tool may use an XLSX reader only in the source-normalization/build path. Normal application execution and normalized-package import must not require XLSX parsing or network access.

If an XLSX library is added, keep it out of runtime dependencies where the project tooling supports that separation.

The build tool must fail closed on unexpected workbook structure, duplicate headers/components, unknown value-origin semantics or count mismatches rather than adapting heuristically.

## Deliberate boundaries

Not authorized in this slice:

- Market Catalog product/SKU acquisition or price scraping;
- automatic matching of merchant Product Cards to BLS foods;
- changing Product Card edible-mass rules or nutrient-override semantics;
- new DGE/ÖGE target mappings;
- optimizer-policy changes;
- NIDDK/Hall weight-change execution;
- pediatric/infant execution;
- UI/API/authentication;
- runtime BLS synchronization;
- saved Purchase Plan history.

## Required completion evidence

Before this slice is complete:

- official BLS 4.0 source identity, exact file digests and CC BY 4.0 attribution are recorded;
- normalized package rebuild from the pinned source inputs is byte-reproducible;
- production package contains exactly 7,140 distinct BLS food codes and 138 distinct component definitions, unless the pinned official source itself is demonstrably corrected and the source identity is updated explicitly;
- every imported food resolves to exactly one ADR-005 top-level category with no name-based inference;
- every normalized nutrient code exists in the component catalog and uses its canonical native unit/basis;
- missing / trace / logical-zero / computed-zero / known positive cases are covered by parser and persistence tests;
- source precision, value-origin and reference provenance round-trip losslessly enough to audit normalized values;
- migration succeeds from current `main` schema and from an empty database;
- import is transactional, idempotent for identical content and rejects conflicting same-version content;
- representative production BLS foods round-trip through `FoodKnowledgeRepository` and the Planning Snapshot path;
- active `mvp-v1` mapped components can consume BLS food evidence without name matching or unit guessing;
- existing first-slice fixtures, `mvp-v1` target derivation, solver and architecture-boundary regressions remain green;
- CI verifies normalized package integrity/reproducibility without runtime network access.

## Readiness review

S2: `PASS`; no new semantic decision is required to start this bounded implementation.

S3: `PASS`; existing modular monolith, Food Knowledge ownership and relational store remain valid.

S4 P0: `0`.
S4 P1: `0`.

Non-blocking risks:

- **P2** — source XLSX download endpoints may be tokenized/rotated; mitigate with DOI/version/file digest identity and offline pinned inputs, not runtime URL dependence;
- **P2** — explicit classification of all BLS foods into the ADR-005 taxonomy is review-heavy; mitigate with deterministic prefix rules, narrow overrides and exact-one coverage tests;
- **P2** — the normalized production package is materially larger than the nutrition-standard package; shard deterministically and omit only semantically `missing` cells;
- **P2** — BLS provenance/reference strings may be heterogeneous; preserve source text rather than normalizing it into unsupported semantics.

Implementation readiness: **PASS** for this bounded BLS 4.0 Food Knowledge source-data/import slice.

## Next

After this planning/readiness PR is squash-merged, create a fresh implementation branch from the resulting `main` SHA and implement only the source normalization, deterministic package, Food Knowledge persistence/import and regression work authorized above.