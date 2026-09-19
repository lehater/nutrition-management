# BLS 4.0 verified source-byte evidence

Status: retained provenance baseline.

This artifact preserves source facts verified during exact BLS 4.0 input inspection. It is evidence, not active execution state.

## Source identity

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

The official XLSX/PDF files remain external reproducibility inputs.

## Verified workbook structure

Direct OOXML inspection established:

- one main worksheet;
- `7,140` distinct food rows plus one header row;
- `418` main-workbook columns;
- three identification columns followed by `138` value/origin/reference component triplets;
- exactly `138` component definitions in the component workbook;
- exactly `7,140` distinct BLS food codes.

Numeric OOXML cells are serialized as invariant decimal lexical values and carry no custom numeric display format in the inspected workbook. Raw extraction therefore preserves the exact OOXML lexical numeric representation before Decimal conversion and never routes it through binary floating-point reconstruction.

## Source cases observed

The main workbook contains:

- `1,806` literal `TR` values;
- `746` literal `<LOQ` values;
- `2,733` literal `<LOD` values;
- `392` literal `<LOD or <LOQ` values.

Additional observed source cases include:

- analytical-limit/trace markers with `-` origin;
- blank/missing cells carrying origin/reference metadata;
- defects covered by the August 2026 errata, including direct and propagated corrections.

These observations motivate ADR-015 and do not authorize heuristic repair.

## Derived build boundary

The accepted source-processing order is:

`exact pinned XLSX bytes -> lossless OOXML raw extraction -> pinned ADR-014 errata overlay and deterministic recomputation -> strict ADR-013/ADR-015 semantic normalization -> deterministic package`.

The extractor owns structure and lexical preservation only. Correction owns authoritative repair. Semantic normalization owns evidence classification and vocabulary validation. Package generation owns deterministic ordering, manifests and digests.
