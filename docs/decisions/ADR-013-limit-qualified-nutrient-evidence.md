# ADR-013 — Limit-qualified nutrient evidence remains distinct from trace and missing

Status: `accepted`.

Date: 2026-09-16.
Lifecycle owner: `S2 Strategic/Tactical Domain Design / Food Knowledge`.

## Context

ADR-004 currently distinguishes numeric known amount, known/logical zero, trace/present-but-not-quantitatively-known and missing/unknown composition evidence.

Inspection of the official BLS 4.0 documentation reveals two additional source meanings. In addition to numeric values, `TR` (`Spuren`) and missing values, BLS may report `<LOQ` or `<LOD`. BLS documents these separately from `Spuren`: `TR` means the nutrient is present but its exact amount is unknown, while `<LOQ` and `<LOD` communicate measurement-limit qualification.

Collapsing `<LOQ` or `<LOD` into `trace`, `missing` or numeric zero would destroy source meaning. Treating them as numeric amounts would also let Purchase Planning claim deterministic coverage from a quantity the source does not quantify.

BLS 4.0 also defines a closed vocabulary of thirteen data-origin categories: `Analyse`, `Rezeptberechnung`, `Musterberechnung`, `Aggregation`, `Literatur`, `Labelangabe`, `Nährstoffdatenbank`, `Übernommener Wert`, `Reskalierung`, `Logische Null`, `Logische Annahme`, `Spuren` and `Formelberechnung`.

## Decision

### Evidence states

Food Knowledge nutrient evidence has six source-preserving states:

1. `known` — a positive quantitative amount is known;
2. `zero` — a quantitative amount of exactly zero is known or asserted by the source;
3. `trace` — presence is asserted, but no quantitative amount is known;
4. `below_quantification_limit` — the source reports `<LOQ`; no deterministic amount is available;
5. `below_detection_limit` — the source reports `<LOD`; no deterministic amount is available;
6. `missing` — no reliable source value is available.

Only `known` and `zero` are quantitatively known. The other four states carry no numeric amount into deterministic nutrition coverage.

`trace`, `below_quantification_limit`, `below_detection_limit` and `missing` remain distinct because they make different evidence claims even though Purchase Planning treats all four as quantitatively unavailable.

### BLS 4.0 normalization

BLS normalization uses source semantics before numeric coercion:

- `Spuren` / `TR` -> `trace`, with no numeric amount;
- `<LOQ` -> `below_quantification_limit`, with no numeric amount;
- `<LOD` -> `below_detection_limit`, with no numeric amount;
- absent nutrient value with no contradictory evidence -> `missing`;
- numeric zero with a non-trace origin -> `zero`;
- positive numeric value -> `known`;
- negative values are rejected.

A `Logische Null` record must normalize to `zero`. A trace or limit-qualified marker must not become zero even if a source representation contains a numeric-looking zero alongside the qualifier.

The exact original source marker/value text, data-origin category and source reference remain provenance.

### Data-origin vocabulary

The BLS 4.0 normalization boundary accepts only the thirteen documented data-origin categories listed in Context. An unexpected non-empty origin is a source-structure change and fails closed pending review; it is not silently treated as an existing category.

### Cross-context consequence

Food Knowledge publishes the extended evidence state. Market Catalog preserves it when no SKU nutrient override replaces the component. Purchase Planning treats any state other than `known` or `zero` as quantitatively unavailable for deterministic target/safety arithmetic.

This decision does not create a numeric estimate for trace, LOQ or LOD evidence. If probabilistic/bounded optimization is later required, that is a separate policy decision.

## Consequences

- BLS 4.0 source meaning can be represented without collapsing measurement-limit evidence into trace or missing.
- Existing `known`, `zero`, `trace` and `missing` semantics remain compatible; two non-quantitative states are added.
- Food Knowledge contracts/domain model, persistence validation, Market Catalog projection, Purchase Planning evidence handling and reporting tests must accept the extended state set.
- Deterministic optimization remains conservative: LOQ/LOD evidence cannot satisfy a quantitative target or prove a quantitative safety contribution.
- Build/import tooling can fail closed on an unknown BLS data-origin category instead of guessing.

## Alternatives considered

### Map `<LOQ` and `<LOD` to `trace`

Rejected because BLS explicitly distinguishes `Spuren` from measurement-limit qualification. In particular, `<LOD` does not make the same positive-presence assertion as `Spuren`.

### Map `<LOQ` and `<LOD` to `missing`

Rejected because a measurement-limit statement is evidence and is more specific than absence of reliable data.

### Store the distinction only in raw provenance while publishing `missing`

Rejected because the published Food Knowledge fact would then misstate the evidence semantics and downstream reporting could not distinguish source uncertainty classes.

### Introduce numeric LOQ/LOD bounds immediately

Rejected for this slice because the BLS display marker does not by itself provide a canonical numeric bound in the normalized food fact. Bound-aware optimization would require additional source semantics and policy.

## Supersession

Supersedes: the four-state-only scope of the `Unknown, trace and zero` subsection of ADR-004.
Superseded by: ADR-015 for the exhaustive evidence-state set when the source reports the combined `<LOD or <LOQ` marker.
