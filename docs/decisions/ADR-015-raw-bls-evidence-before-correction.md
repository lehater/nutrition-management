# ADR-015 — Preserve raw BLS evidence before correction and represent ambiguous analytical-limit markers

Status: `accepted`.

Date: 2026-09-17.
Lifecycle owner: `S2 Strategic/Tactical Domain Design / Food Knowledge source semantics`.

## Context

ADR-013 introduced six normalized Food Knowledge evidence states after documentation-level inspection of BLS 4.0: `known`, `zero`, `trace`, `below_quantification_limit`, `below_detection_limit` and `missing`. ADR-014 requires official BLS errata to be applied as explicit typed correction overlays while preserving the immutable identity of the published BLS 4.0 files.

Inspection of the exact official BLS 4.0 source bytes exposed two additional facts:

1. the main workbook contains `392` nutrient cells whose published marker is the single literal value `<LOD or <LOQ`;
2. the published workbook contains source defects/inconsistencies that the August 2026 official errata is intended to correct, including raw missing/malformed cells with origin/reference metadata.

The combined marker cannot be represented source-faithfully by choosing either exact `<LOD` or exact `<LOQ`. The raw defects also mean strict normalized-evidence validation cannot run before the authoritative correction overlay.

The raw OOXML source uses `-` as an absence sentinel in origin/reference cells. It is not a fourteenth BLS origin category.

## Decision

### Raw source evidence is a separate build-stage representation

The BLS build path has an explicit raw extraction representation that preserves, per food/component triplet:

- BLS food code;
- component code;
- raw source value lexical text or absence;
- raw origin text or absence sentinel;
- raw reference text or absence sentinel;
- source file identity.

Raw source evidence is not yet a canonical `NutrientEvidence` claim. It may contain combinations that are invalid under the normalized Food Knowledge contract because official errata may repair them.

### Correction order is fixed

The source-normalization chain is:

`pinned XLSX bytes -> lossless raw extraction -> pinned official errata overlay / deterministic propagation -> strict semantic normalization -> deterministic package`.

Strict normalized-evidence validation runs only after all applicable ADR-014 corrections and deterministic recomputations have been applied.

A correction registry never mutates the pinned raw input bytes. Source identity and correction provenance remain separate.

### Ambiguous analytical-limit evidence is explicit

Food Knowledge adds one source-preserving non-quantitative evidence state:

`below_detection_or_quantification_limit`.

It represents the literal BLS marker `<LOD or <LOQ` when the source does not identify which analytical limit applies.

The state carries no numeric amount and must not be narrowed to either exact `<LOD` or exact `<LOQ`.

Together with ADR-013, normalized Food Knowledge evidence states are:

1. `known`;
2. `zero`;
3. `trace`;
4. `below_quantification_limit`;
5. `below_detection_limit`;
6. `below_detection_or_quantification_limit`;
7. `missing`.

Only `known` and `zero` are quantitatively usable in deterministic Purchase Planning.

### Origin sentinel is not an origin category

The closed thirteen-category BLS origin vocabulary from ADR-013 remains unchanged.

A raw origin cell containing `-` or no cell value means that no BLS origin category is supplied. It is represented as absent origin provenance.

A source marker such as `TR`, `<LOD`, `<LOQ` or `<LOD or <LOQ` may still establish its evidence state when raw origin is absent, provided the corrected/raw evidence does not contradict another source fact. Unexpected non-sentinel, non-vocabulary origin text still fails closed.

### Missing raw values may retain metadata until correction

A raw missing value may carry origin/reference text because the published workbook contains known inconsistencies. Raw extraction preserves such text. After the official correction overlay, strict normalization decides whether the effective value remains `missing` or becomes another evidence state.

## Consequences

- Exact official 4.0 bytes can be ingested without hidden repairs or premature rejection.
- `<LOD or <LOQ` remains distinguishable from exact `<LOD` and `<LOQ`.
- Purchase Planning remains conservative because the new state is non-quantitative.
- BLS origin governance remains closed; `-` is absence, not vocabulary.
- Workbook extraction and correction are distinct build-time responsibilities.
- Package validation remains strict because only post-correction normalized evidence enters the production package.

## Alternatives considered

### Map `<LOD or <LOQ` to one exact limit state

Rejected because it narrows source uncertainty.

### Map `<LOD or <LOQ` to `missing`

Rejected because the source provides analytical-limit evidence more specific than absence.

### Run strict normalization before applying errata

Rejected because authoritative source defects must remain representable until the authoritative correction stage.

### Treat `-` as a fourteenth origin category

Rejected because it is an absence sentinel rather than a documented provenance category.

## Supersession

Supersedes: the six-state exhaustive scope of ADR-013 for the newly observed combined `<LOD or <LOQ` marker and clarifies its interaction with ADR-014 correction ordering.
Superseded by: none.
