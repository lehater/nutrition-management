# Active execution

Current product work: resolve the BLS 4.0 source-semantics gap discovered during draft implementation PR #11, then resume the bounded Food Knowledge import slice.

Lifecycle state: **S2 PASS / S4 PASS as amended** under ADR-012, ADR-013 and [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md).
Implementation authorization after this decision PR merges: **only** [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md) as amended by [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md).

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; ADR-004 remains the BLS 4.0 canonical nutrient anchor, ADR-012 extends Food Knowledge evidence semantics for `<LOQ`/`<LOD`, and ADR-013 defines authoritative BLS errata overlays.
- S3 Architecture: `PASS`; existing modular monolith, Food Knowledge ownership and one relational store remain valid.
- S4 Implementation Readiness: `PASS` as amended after implementation-time source inspection.
- Previous `mvp-v1` Nutrition Standard Set slice: completion gate `PASS`, squash-merged as commit `93b44914913ec9b8bdfdfd69d9bd48cc2fefaf4a` via PR #9.
- Original BLS readiness packet: squash-merged as commit `f1f8e0f06bc46c493f1ad73998e68741f7c0c2bb` via PR #10.
- Draft implementation PR #11 remains open and must not merge until the amended semantics and production completion gates pass.

## Source-inspection correction

Official BLS 4.0 documentation distinguishes six evidence outcomes needed by Food Knowledge:

- `known`;
- `zero`;
- `trace` (`Spuren` / `TR`);
- `below_quantification_limit` (`<LOQ`);
- `below_detection_limit` (`<LOD`);
- `missing`.

Only `known` and `zero` are quantitatively known. Purchase Planning must treat the other four states as quantitatively unavailable while preserving their distinct evidence meanings.

The BLS normalizer also accepts only the thirteen documented BLS 4.0 data-origin categories and fails closed on unexpected source semantics.

MRI additionally published a February 2026 BLS 4.0 erratum for food `M111100`. The production normalized package must apply it through an explicit versioned correction registry while retaining the original workbook digests:

- `RETOL = 2.4 µg/100 g`;
- `VITA = 3.1 µg/100 g`;
- `VITAA = 2.7 µg/100 g`.

## Authorized implementation outcome

`official pinned BLS 4.0 XLSX inputs + authoritative correction registry -> deterministic normalized Food Knowledge package -> transactional/idempotent production import -> BLS-backed Base Food facts available through existing planning boundary`.

The implementation preserves:

- BLS 4.0 component codes/native units and `100 g edible portion` basis;
- all 138 component definitions;
- all six accepted evidence states without semantic collapse;
- per-value origin/reference/raw-value provenance;
- deterministic `bls:4.0:<BLS_CODE>` Base Food identity;
- explicit project-owned category mapping with exact-one classification coverage;
- immutable raw source digests plus explicit authoritative correction provenance.

## Remaining completion dependencies

Completion still requires:

- exact official BLS 4.0 XLSX bytes and SHA-256 digests;
- deterministic normalized package rebuild evidence;
- exactly 7,140 distinct BLS food codes and 138 component definitions unless the pinned official source identity is explicitly revised;
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
Open P1: `0` at the amended readiness level; implementation PR #11 must implement ADR-012/ADR-013 before it can leave draft.

## Next

Squash-merge this semantic-correction decision PR after CI/review. Then resume draft PR #11 by implementing the six-state evidence contract, closed BLS origin vocabulary and correction-registry validation before any XLSX-specific normalizer or production corpus work.
