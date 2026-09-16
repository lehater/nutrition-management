# ADR-014 — Preserve raw BLS evidence before correction and represent ambiguous analytical-limit markers

Status: `accepted`.

Date: 2026-09-17.
Lifecycle owner: `S2 Strategic/Tactical Domain Design / Food Knowledge source semantics`.

## Context

ADR-012 introduced six normalized Food Knowledge evidence states after documentation-level inspection of BLS 4.0: numeric known, zero, trace, below quantification limit (`<LOQ`), below detection limit (`<LOD`) and missing. ADR-013 requires official BLS errata to be applied as explicit typed correction overlays while preserving the immutable identity of the published BLS 4.0 files.

Inspection of the exact official BLS 4.0 source bytes exposed two additional facts that the documentation-only review could not prove:

1. the main workbook contains `392` nutrient cells whose published marker is the single literal value `<LOD or <LOQ>`;
2. the published 4.0 workbook contains source defects/inconsistencies that the August 2026 official errata is specifically intended to correct, including raw missing/malformed cells with origin/reference metadata.

The first case cannot be represented source-faithfully by choosing either ADR-012 state `below_detection_limit` or `below_quantification_limit`. The second case means strict normalized-evidence validation cannot run before the official correction overlay: doing so would reject the very raw source defects that ADR-013 requires the build to correct deterministically.

The raw OOXML source also uses `-` as a sentinel for absent value/origin/reference information. In a small number of published rows a trace or limit marker is present while the origin field is `-`. The sentinel is absence of an origin category, not a fourteenth BLS data-origin category.

## Decision

### Raw source evidence is a separate build-stage representation

The BLS build path has an explicit raw extraction representation that preserves, per food/component triplet:

- BLS food code;
- component code;
- raw source value lexical text or absence;
- raw origin text or absence sentinel;
- raw reference text or absence sentinel;
- source file identity.

Raw source evidence is not yet a canonical `NutrientEvidence` claim. It may contain combinations that are invalid under the normalized Food Knowledge contract because official errata exists precisely to repair some published 4.0 combinations.

### Correction order is fixed

The source-normalization chain is:

`pinned XLSX bytes -> lossless raw extraction -> pinned official errata overlay / deterministic propagation -> strict semantic normalization -> deterministic package`.

Strict normalized-evidence validation therefore runs **after** all applicable ADR-013 corrections and deterministic recomputations have been applied.

A correction registry does not mutate the pinned raw input bytes. The build retains source digest identity and correction provenance separately.

### Ambiguous analytical-limit evidence is explicit

Food Knowledge adds one source-preserving non-quantitative evidence state:

`below_detection_or_quantification_limit`.

It represents the literal BLS marker `<LOD or <LOQ>` when the source does not identify which analytical limit applies.

The state does not assert a numeric amount and must not be collapsed into either exact `<LOD>` or exact `<LOQ>` semantics. The exact raw marker remains provenance.

Together with ADR-012, the normalized Food Knowledge evidence states are now:

1. `known`;
2. `zero`;
3. `trace`;
4. `below_quantification_limit`;
5. `below_detection_limit`;
6. `below_detection_or_quantification_limit`;
7. `missing`.

Only `known` and `zero` are quantitatively usable in deterministic Purchase Planning. All five other states contribute no numeric amount and preserve their distinct evidence claim.

### Origin sentinel is not an origin category

The closed BLS origin vocabulary from ADR-012 remains unchanged at thirteen categories.

A raw origin cell containing `-` or no cell value means that no BLS origin category is supplied. It is represented as absent origin provenance, not as an additional category.

A source marker such as `TR`, `<LOD>`, `<LOQ>` or `<LOD or <LOQ>` may still establish its evidence state when the raw origin is absent, provided the corrected/raw combination does not contradict another source fact. Unexpected non-sentinel, non-vocabulary origin text still fails closed.

### Missing raw values may retain raw metadata until correction

A raw missing value may carry origin/reference text because the published 4.0 workbook contains known inconsistencies. The raw extraction stage preserves such text. After the official correction overlay, strict normalization decides whether the effective value remains `missing` or becomes another evidence state.

A final normalized `missing` fact does not need a persisted nutrient-value row, consistent with the existing deterministic-package contract; the committed correction/coverage artifacts remain the audit record for any corrected raw anomaly.

## Consequences

- The exact official 4.0 bytes can be ingested without inventing repairs or rejecting authoritative-but-known-defective source rows before errata is applied.
- `<LOD or <LOQ>` remains distinguishable from exact `<LOD>` and exact `<LOQ>` instead of being silently narrowed.
- Purchase Planning remains deterministic and conservative because the new state is non-quantitative.
- BLS origin governance remains closed; `-` is treated as absence rather than extending the vocabulary.
- The workbook reader/extractor and correction engine become distinct build-time responsibilities.
- Package validation remains strict because only post-correction normalized evidence enters the production package.
- Existing normalized fixtures remain valid; a seventh evidence state is additive.

## Alternatives considered

### Map `<LOD or <LOQ>` to `below_quantification_limit`

Rejected because it loses the source's explicit uncertainty over which analytical limit was reported and weakens ADR-012's source-preservation rationale.

### Map `<LOD or <LOQ>` to `missing`

Rejected because the source provides analytical-limit evidence that is materially more specific than absence of data.

### Run strict semantic validation before applying errata

Rejected because the current official BLS 4.0 bytes contain precisely the malformed/source-defect cases documented by the official errata. Validation-before-correction would make authoritative corrections impossible to apply without parser exceptions or hidden special cases.

### Treat `-` as a fourteenth data-origin category

Rejected because the BLS documentation defines thirteen origin categories; `-` is a missing-value/sentinel representation, not a provenance category.

## Supersession

Supersedes: the six-state exhaustive scope of ADR-012 only for the newly observed combined `<LOD or <LOQ>` marker and clarifies the correction-order interaction with ADR-013.
Superseded by: none.
