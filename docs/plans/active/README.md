# Active execution

Current product work: implement the authorized BLS 4.0 Food Knowledge source-data/import slice under the accepted semantic amendment.

Lifecycle state: **Implementation IN_PROGRESS** under S2/S3/S4 `PASS` as amended by ADR-012, ADR-013 and [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md).
Implementation authorization: **only** [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md) as amended by [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md).
Original implementation base: `f1f8e0f06bc46c493f1ad73998e68741f7c0c2bb` (PR #10 squash merge).
Semantic amendment base incorporated from `006ef8e86e51aedcd1c1028cf4691019799fc14f` (PR #12 squash merge).

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; ADR-004 remains the BLS 4.0 canonical nutrient anchor, ADR-012 defines six source-preserving evidence states, and ADR-013 defines authoritative typed BLS errata overlays with complete coverage accounting.
- S3 Architecture: `PASS`; existing modular monolith, Food Knowledge ownership and one relational store remain valid.
- S4 Implementation Readiness: `PASS` as amended after implementation-time source inspection.
- Previous `mvp-v1` Nutrition Standard Set slice: completion gate `PASS`, squash-merged as commit `93b44914913ec9b8bdfdfd69d9bd48cc2fefaf4a` via PR #9.
- Original BLS readiness packet: squash-merged as commit `f1f8e0f06bc46c493f1ad73998e68741f7c0c2bb` via PR #10.
- BLS semantic amendment: squash-merged as commit `006ef8e86e51aedcd1c1028cf4691019799fc14f` via PR #12.
- Draft implementation PR #11 remains open and must not merge until all production completion gates pass.

## Authorized implementation outcome

`official pinned BLS 4.0 XLSX inputs + pinned current official errata + authoritative typed correction registry -> deterministic normalized Food Knowledge package -> transactional/idempotent production import -> BLS-backed Base Food facts available through existing planning boundary`.

The implementation preserves:

- BLS 4.0 component codes/native units and `100 g edible portion` basis;
- all 138 component definitions;
- six evidence states: `known`, `zero`, `trace`, `below_quantification_limit`, `below_detection_limit`, `missing`;
- only `known` and `zero` as quantitatively usable in deterministic Planning;
- the closed thirteen-category BLS data-origin vocabulary with fail-closed handling;
- per-value origin/reference/raw-value provenance;
- deterministic `bls:4.0:<BLS_CODE>` Base Food identity;
- explicit project-owned category mapping with exact-one classification coverage;
- immutable raw source digests plus explicit authoritative correction provenance and full errata coverage accounting.

## Implemented structural increment

Draft PR #11 currently contains:

- Food Knowledge persistence migration `0005` for source/component/value provenance;
- source-rich BLS dataset/component models and repository persistence;
- deterministic normalized-package validation and idempotent import using fixtures;
- canonical BLS Base Food identity generation;
- six-state Food Knowledge and Purchase Planning evidence contracts;
- conservative Planning/reporting/safety/solver handling for every non-quantitative state;
- fail-closed BLS value/origin normalization helpers;
- typed correction and errata-coverage package schema/validation;
- regression tests for package tampering, category gaps, persistence provenance, LOQ/LOD semantics, safety and solver behavior.

## Remaining completion dependencies

Completion still requires:

- exact official BLS 4.0 XLSX bytes and SHA-256 digests;
- exact current official August 2026 errata bytes and SHA-256 digest;
- deterministic XLSX normalization tooling and byte-reproducible package rebuild evidence;
- exactly 7,140 distinct BLS food codes and 138 component definitions unless the pinned official source identity is explicitly revised;
- complete current-errata coverage with no silent unsupported correction type;
- exact-one ADR-005 category classification for every imported food;
- representative production BLS foods round-tripping through `FoodKnowledgeRepository` and Planning Snapshot;
- full regression/CI success without runtime network access.

No digest, source corpus, category decision or source correction may be fabricated.

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
Open P1: semantic-amendment implementation is expected to be closed by the current structural increment; final status depends on CI/review of the synchronized head.

## Next

Run full CI on the branch synchronized with PR #12. Fix only concrete P0/P1 regressions. After the structural head is green, implement the deterministic XLSX normalizer and production-source package boundary; do not expand scope beyond the authorized slice.