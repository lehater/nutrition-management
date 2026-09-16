# ADR-013 — Official BLS errata are applied as explicit source-correction overlays

Status: `accepted`.

Date: 2026-09-16.
Lifecycle owner: `S2 Strategic/Tactical Domain Design / Food Knowledge source governance`.

## Context

The BLS 4.0 production baseline is pinned to the official 2025 source package by version, DOI and exact input-file digests. After that package was published, the Max Rubner-Institut issued an official February 2026 erratum for food `M111100` (fresh skimmed milk, at most 0.1% fat, pasteurized).

The erratum states that the published retinol value was taken from fortified milk by mistake and requires corrected values for all analyses until the next BLS update. It provides corrected values per 100 g for `RETOL` (2.4 µg), `VITA` (3.1 µg) and `VITAA` (2.7 µg), with the latter two following from formula calculation.

Importing the raw 2025 workbook unchanged as the production baseline would therefore reproduce a known source defect. Silently changing the workbook-derived values without recording the correction would break reproducibility and provenance.

## Decision

### Source identity remains immutable

The pinned BLS 4.0 XLSX files retain their own SHA-256 identities. An official erratum does not rewrite or masquerade as those original source bytes.

### Corrections are explicit overlays

Food Knowledge normalization supports a deterministic, versioned source-correction registry applied after raw source extraction and before generation of the normalized production package.

Each correction records at least:

- correction/erratum identity and publication date;
- official source locator;
- affected BLS food code and component code;
- original source value/qualifier when available from the pinned input;
- corrected normalized source value/qualifier;
- corrected data-origin/reference semantics when the erratum specifies them;
- rationale/source note.

The correction registry is part of the normalized package file inventory and therefore part of the package digest.

### Only authoritative corrections qualify

A correction overlay may be applied automatically only when it is published by the same authoritative source owner for the pinned data set (MRI for BLS) or is otherwise accepted by a separate project decision. Community reports or heuristic repairs do not enter the production package automatically.

### BLS 4.0 February 2026 erratum

The BLS 4.0 production package must apply the MRI February 2026 erratum for `M111100` before the slice completion gate passes:

- `RETOL` -> `2.4 µg/100 g`;
- `VITA` -> `3.1 µg/100 g`;
- `VITAA` -> `2.7 µg/100 g`.

The normalized package must retain enough correction provenance to show that these values differ intentionally from the pinned 2025 workbook and why.

### Version upgrades remain separate

When MRI publishes a new BLS release whose source bytes already include the correction, that later release is adopted under its own explicit source/version identity. The 4.0 correction overlay is not silently carried forward unless source review shows it remains applicable.

## Consequences

- Production planning does not knowingly consume the published 4.0 milk error.
- Reproducibility remains intact because raw source digests and correction-overlay digest are both explicit.
- Package generation gains one additional fail-closed input: the versioned official-correction registry.
- Persistence may retain only the effective normalized value plus correction/source provenance; the committed deterministic package remains the audit record for original-versus-corrected source values.
- Future official errata can be incorporated without mutating historical input-file identity or inventing a pseudo BLS version.

## Alternatives considered

### Import the pinned workbook literally and ignore later errata

Rejected because MRI explicitly requires the corrected values for analyses until the next update; reproducing a known erroneous value is not a useful production baseline.

### Edit or replace the downloaded XLSX before hashing it

Rejected because that destroys the identity of the official input bytes and makes the package falsely appear to come directly from the published workbook.

### Treat the erratum as a new BLS version

Rejected because MRI has not assigned a new BLS version to this correction. Project source identity must not invent external versioning.

### Hard-code corrected values directly in parser code

Rejected because corrections are data/provenance, not parser behavior. A versioned correction registry is reviewable, reproducible and extensible.

## Supersession

Supersedes: none.
Superseded by: none.
