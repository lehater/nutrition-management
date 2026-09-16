# Active execution

Current product work: resolve the final BLS 4.0 source-byte semantic gap discovered during draft implementation PR #11, then resume deterministic production package generation.

Lifecycle state: **S2 PASS / S4 PASS as amended** under ADR-012, ADR-013, ADR-014, [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md) and [`bls-v4-food-knowledge-source-bytes-amendment.md`](bls-v4-food-knowledge-source-bytes-amendment.md).
Implementation authorization after this decision PR merges: **only** [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md) as amended by the two BLS amendment documents above.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; ADR-004 remains the BLS 4.0 canonical nutrient anchor, ADR-012 defines analytical-limit evidence, ADR-013 defines authoritative BLS errata overlays, and ADR-014 fixes raw-source/correction ordering plus the combined `<LOD or <LOQ` source state.
- S3 Architecture: `PASS`; existing modular monolith, Food Knowledge ownership and one relational store remain valid.
- S4 Implementation Readiness: `PASS` as amended after exact official source-byte inspection.
- Previous `mvp-v1` Nutrition Standard Set slice: completion gate `PASS`, squash-merged as commit `93b44914913ec9b8bdfdfd69d9bd48cc2fefaf4a` via PR #9.
- Original BLS readiness packet: squash-merged as commit `f1f8e0f06bc46c493f1ad73998e68741f7c0c2bb` via PR #10.
- First BLS semantic amendment: squash-merged as commit `006ef8e86e51aedcd1c1028cf4691019799fc14f` via PR #12.
- Draft implementation PR #11 remains open and must not merge until the amended semantics and production completion gates pass.

## Verified official source pins

Exact official build-time source bytes are now available and pinned:

- `BLS_4_0_2025_DE.zip`: `12b7a6ba62807ec9b301eb276f897dc85f99b2292311618dec3749a12d984c91`;
- `BLS_4_0_Daten_2025_DE.xlsx`: `524bbefe25b691f5cb3de7a9f3e27fa2967aebfeabf217d99414ba7806e78c60`;
- `BLS_4_0_Components_DE_EN.xlsx`: `359aefcd2086f45e62ff3dbd0c8536306e594a5806ac325d8bf86f484561bdf4`;
- `BLS_4_0_Dokumentation_DE.pdf`: `6d83913f9b705399f86795a9c3afcb2d0454d1129bfb24ce53da911c5a6a24b6`;
- current `Erratum_BLS_4_0_DE.pdf`, state August 2026: `ae021760436f1b6af09fd1df46e93b64d94e415f0a3b665e1d901cdee4ddd8c3`.

Direct OOXML inspection confirms `7,140` distinct foods, `138` components and the documented `418`-column main schema.

## Source-byte semantic correction

The exact main workbook contains the documented exact markers plus `392` literal `<LOD or <LOQ` cells. ADR-014 therefore adds:

- `below_detection_or_quantification_limit` as a distinct non-quantitative evidence state;
- raw triplet extraction before corrections/normalization;
- `-` as an absence sentinel rather than a fourteenth data-origin category;
- fixed build order `raw XLSX -> official errata overlay/recomputation -> strict normalization -> deterministic package`.

Only `known` and `zero` remain quantitatively usable by deterministic Purchase Planning. All analytical-limit, trace and missing states remain non-quantitative.

## Authorized implementation outcome

`exact pinned BLS 4.0 XLSX inputs + exact pinned August-2026 errata -> lossless raw extraction -> authoritative typed corrections/recomputation with complete errata coverage -> deterministic normalized Food Knowledge package -> transactional/idempotent production import -> BLS-backed Base Food facts available through existing planning boundary`.

The implementation preserves:

- BLS 4.0 component codes/native units and `100 g edible portion` basis;
- all 138 component definitions;
- all seven accepted evidence states without semantic collapse;
- exact raw source lexical value/origin/reference evidence through the build audit boundary;
- deterministic `bls:4.0:<BLS_CODE>` Base Food identity;
- explicit project-owned category mapping with exact-one classification coverage;
- immutable source digests plus complete authoritative correction provenance/coverage.

## Remaining completion dependencies

Source acquisition is no longer a blocker. Completion now requires:

- repository build tooling that reads the pinned OOXML losslessly and applies corrections before strict normalization;
- complete August-2026 errata coverage derived from the pinned errata artifact, including formula/recipe propagation where required;
- deterministic normalized package rebuild evidence;
- exactly 7,140 distinct BLS food codes and 138 component definitions;
- exact-one ADR-005 category classification for every imported food;
- representative production BLS foods round-tripping through `FoodKnowledgeRepository` and Planning Snapshot;
- full regression/CI success without runtime network access.

No source correction or category decision may be fabricated.

## Guardrails

This slice does not authorize:

- Market Catalog price/product acquisition or automatic SKU-to-BLS matching;
- optimizer-policy changes;
- new Nutrition Targeting mappings;
- NIDDK/Hall execution;
- pediatric/infant execution;
- UI/API/authentication;
- runtime BLS synchronization;
- saved Purchase Plan history.

Open P0: `0`.
Open P1: `0` at the amended readiness level; implementation PR #11 must implement ADR-014 before it can leave draft.

## Next

Squash-merge this narrow source-byte semantic decision PR after CI/review. Then sync draft PR #11, implement the raw-extraction/correction/normalization separation and seventh evidence state, and proceed to complete errata/category/package generation from the pinned official inputs.
