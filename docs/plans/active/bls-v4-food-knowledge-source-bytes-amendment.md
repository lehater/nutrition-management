# BLS 4.0 Food Knowledge slice — verified source-bytes amendment

Status: `PASS` — S2/S4 amendment after inspection of exact official source bytes.
Lifecycle owner: Food Knowledge / S4 Implementation Readiness.

This amendment is read together with [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md) and [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md). ADR-014 is authoritative where the earlier documents assumed that strict semantic normalization could run directly on each published XLSX triplet or that the six ADR-012 states were exhaustive.

## Verified official source identity

The exact official BLS 4.0 package and current official errata were acquired from MRI/BLS download endpoints as build-time evidence. Rotating/tokenized URLs are not retained as identity boundaries.

Pinned identities:

- BLS version: `4.0`;
- DOI: `10.25826/Data20251217-134202-0`;
- official source page: `https://www.blsdb.de/download`;
- package ZIP filename: `BLS_4_0_2025_DE.zip`;
- package ZIP SHA-256: `12b7a6ba62807ec9b301eb276f897dc85f99b2292311618dec3749a12d984c91`;
- main workbook `BLS_4_0_Daten_2025_DE.xlsx` SHA-256: `524bbefe25b691f5cb3de7a9f3e27fa2967aebfeabf217d99414ba7806e78c60`;
- component workbook `BLS_4_0_Components_DE_EN.xlsx` SHA-256: `359aefcd2086f45e62ff3dbd0c8536306e594a5806ac325d8bf86f484561bdf4`;
- bundled documentation `BLS_4_0_Dokumentation_DE.pdf` SHA-256: `6d83913f9b705399f86795a9c3afcb2d0454d1129bfb24ce53da911c5a6a24b6`;
- current official errata filename: `Erratum_BLS_4_0_DE.pdf`;
- errata state: `August 2026`;
- errata SHA-256: `ae021760436f1b6af09fd1df46e93b64d94e415f0a3b665e1d901cdee4ddd8c3`.

The official XLSX files remain external reproducibility inputs; the production repository commits the deterministic normalized package and source digests, not the source XLSX bytes.

## Verified workbook structure

Direct OOXML inspection confirms the documented production counts and structure:

- one main worksheet;
- `7,140` distinct data rows plus one header row;
- `418` columns in the main schema;
- first three identification columns are BLS code / German name / English name;
- `138` component triplets follow as value / data origin / reference;
- exactly `138` component definitions are present in the nine-column component reference workbook;
- the main workbook contains exactly `7,140` distinct BLS food codes.

Numeric cells in the OOXML payload are serialized as invariant decimal lexical values such as `11.45` and carry no custom numeric display format. Build-time raw extraction therefore preserves the exact OOXML lexical numeric representation; semantic Decimal conversion must not round it. Documentation-level comma decimal examples remain accepted when source text is supplied in that form, but locale rendering is not reconstructed from the XLSX.

## Source cases discovered only from exact bytes

The published main workbook contains:

- `1,806` literal `TR` values;
- `746` literal `<LOQ` values;
- `2,733` literal `<LOD` values;
- `392` literal `<LOD or <LOQ` values.

The combined marker is a distinct source claim and is represented by ADR-014 as `below_detection_or_quantification_limit`.

The workbook also contains raw inconsistencies relevant to correction order, including:

- some analytical-limit/trace markers whose origin field is `-`;
- published blank/missing cells that still carry origin/reference metadata;
- source defects explicitly covered by the August 2026 errata, including zinc missing/limit corrections and formula/recipe propagation cases.

These facts require a raw extraction stage before ADR-013 correction overlays. They do not authorize heuristic repair.

## Amended build chain

The authorized deterministic build chain is now:

`exact pinned XLSX bytes -> lossless OOXML raw extraction -> exact pinned August-2026 errata overlay + deterministic recomputation/propagation -> strict normalized evidence/category validation -> deterministic JSON package -> transactional/idempotent import`.

Responsibilities:

- **OOXML extractor**: structure/count validation, shared-string resolution, coordinate-gap preservation, exact source lexical values; no nutrition semantics or corrections.
- **errata overlay**: typed authoritative corrections plus full raw-errata coverage accounting; no mutation of source-file identity.
- **semantic normalizer**: seven-state evidence classification, closed origin vocabulary with `-` treated as absence sentinel, component/category validation.
- **package builder**: deterministic ordering/sharding/manifest digests and byte reproducibility.
- **runtime importer**: offline package validation/persistence only; no XLSX/PDF/network dependency.

## Required regression evidence

Before completion, tests/build evidence must cover:

- exact source digests above;
- 7,140 / 138 / 418 count assertions against the pinned inputs;
- OOXML numeric lexical preservation without float coercion;
- absent physical cells reconstructed by worksheet coordinates rather than positional shifting;
- exact `<LOD or <LOQ` normalization to `below_detection_or_quantification_limit`;
- `-` origin/reference sentinel handling without treating it as a new origin category;
- a raw malformed/known-defect row that is rejected by strict normalization before correction but accepted after an explicit authoritative correction;
- all previously required TR / exact LOQ / exact LOD / zero / known / missing cases;
- complete August-2026 errata coverage derived from the pinned errata artifact rather than only cross-checking two project-authored JSON files.

## Readiness result

S2: `PASS` after ADR-014.
S3: `PASS`; build-stage separation remains inside the existing Food Knowledge infrastructure boundary.
S4: `PASS` as amended.

Open P0: `0`.
Open P1: `0` at readiness level after ADR-014; implementation PR #11 must implement the raw/correction/normalize order and seventh evidence state before production-package completion.

The remaining large work item is no longer acquisition of source bytes. It is deterministic transformation of those pinned inputs: errata coverage, category registry, full normalized package and production E2E.
