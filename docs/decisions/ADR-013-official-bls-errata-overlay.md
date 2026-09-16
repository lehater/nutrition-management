# ADR-013 — Official BLS errata are applied as explicit source-correction overlays

Status: `accepted`.

Date: 2026-09-16.
Lifecycle owner: `S2 Strategic/Tactical Domain Design / Food Knowledge source governance`.

## Context

The BLS 4.0 production baseline is pinned to the official 2025 source package by version, DOI and exact input-file digests. MRI publishes a separate BLS 4.0 errata document containing corrections, error fixes and updates that apply until a later BLS release incorporates them.

The current authoritative errata is `Stand August 2026`. It is broader than the earlier February 2026 milk-only correction: it includes direct nutrient-value corrections, qualifier/data-quality corrections and corrections whose effects propagate through BLS formulas or recipe calculations.

Importing the raw 2025 workbook unchanged would therefore knowingly reproduce source defects. Silently changing workbook-derived values without recording the corrections would break reproducibility and provenance.

## Decision

### Source identity remains immutable

The pinned BLS 4.0 XLSX files retain their own SHA-256 identities. An official erratum does not rewrite or masquerade as those original source bytes.

The exact errata artifact used for a production package is itself pinned by publication state/date, official locator and SHA-256 digest. A rotating download URL is not its identity boundary.

### Corrections are explicit overlays

Food Knowledge normalization supports a deterministic, versioned source-correction registry applied after raw source extraction and before generation of the normalized production package.

The registry supports typed corrections rather than assuming every erratum is one direct cell replacement. A correction may represent at least:

- a direct food/component value or qualifier replacement;
- a source-origin/reference correction;
- a formula or calculation correction whose dependent values must be deterministically recomputed;
- a recipe/derived-value correction whose affected downstream rows are explicitly accounted for.

Each correction record retains enough information to audit the transformation, including:

- correction/errata identity and publication state/date;
- official source locator;
- correction type;
- affected BLS food/component or calculation scope;
- original source value/qualifier when applicable and available from the pinned input;
- corrected source/effective value or rule;
- corrected data-origin/reference semantics when specified;
- rationale/source note.

The correction registry and an errata-coverage record are part of the normalized package file inventory and therefore part of the package digest.

### Full current-errata coverage is mandatory

Production generation applies **all applicable corrections in the pinned current official BLS 4.0 errata**, not a hand-selected subset.

Generation must account for every correction family in the pinned errata as exactly one of:

- applied directly;
- applied through deterministic recomputation/propagation;
- demonstrably not applicable to the pinned source/package, with an explicit reason.

An unsupported correction type or an unaccounted errata entry fails package generation. The implementation must not silently omit a correction because the current registry schema cannot express it.

The August 2026 errata includes the previously published `M111100` milk correction (`RETOL`, `VITA`, `VITAA`) as well as additional corrections. The milk values remain a useful regression case, but they are not the completeness boundary for the overlay.

### Only authoritative corrections qualify

A correction overlay may be applied automatically only when it is published by the same authoritative source owner for the pinned data set (MRI for BLS) or is otherwise accepted by a separate project decision. Community reports or heuristic repairs do not enter the production package automatically.

### Version upgrades remain separate

When MRI publishes a new BLS release whose source bytes incorporate an erratum, that release is adopted under its own explicit source/version identity. A BLS 4.0 overlay is not silently carried forward unless source review shows it remains applicable.

## Consequences

- Production planning does not knowingly consume corrections already published by MRI for BLS 4.0.
- Reproducibility remains intact because raw-source digests, errata-artifact digest, correction registry and coverage accounting are all explicit.
- Package generation gains a fail-closed source-governance input rather than parser hard-coding.
- Correction handling can represent direct values and propagated calculation effects without pretending they are the same operation.
- Persistence may expose only the effective normalized value plus correction/source provenance; the deterministic package remains the full original-versus-corrected audit record.
- A newer official errata replaces the previous errata input for newly generated production packages; historical package digests remain reproducible.

## Alternatives considered

### Import the pinned workbook literally and ignore later errata

Rejected because the source owner explicitly publishes corrections for use before the next BLS release.

### Apply only simple direct-value corrections

Rejected because the current errata contains correction types whose effects are formula- or recipe-derived. Partial support would silently create an internally inconsistent BLS baseline.

### Edit or replace the downloaded XLSX before hashing it

Rejected because that destroys the identity of the official input bytes and makes the package falsely appear to come directly from the published workbook.

### Treat each erratum as a new BLS version

Rejected because MRI has not assigned those corrections a new BLS version. Project source identity must not invent external versioning.

### Hard-code corrected values directly in parser code

Rejected because corrections are source data/provenance and transformation policy, not workbook parser behavior. A versioned registry is reviewable, reproducible and extensible.

## Supersession

Supersedes: none.
Superseded by: none.
