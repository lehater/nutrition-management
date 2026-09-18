# Active execution

Current product work: repair canonical routing and source-precision semantics discovered while exercising draft implementation PR #11, then resume the bounded Food Knowledge import slice.

Lifecycle state: **S2 PASS / S4 PASS as amended** under ADR-013, ADR-014 and [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md).
Implementation authorization remains **only** [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md) as amended by [`bls-v4-food-knowledge-semantic-amendment.md`](bls-v4-food-knowledge-semantic-amendment.md).

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; ADR-004 remains the BLS 4.0 canonical nutrient anchor, ADR-013 extends Food Knowledge evidence semantics for `<LOQ`/`<LOD`, and ADR-014 defines authoritative BLS errata overlays. ADR-012 remains the earlier Nutrition Targeting source-applicability decision.
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

MRI maintains an official BLS 4.0 errata document. The current authoritative state is **August 2026** and is broader than the earlier February milk-only correction. The production normalized package therefore uses a typed correction registry plus explicit errata-coverage accounting, not a hard-coded list of selected replacement cells. Every correction family in the pinned current errata must be applied directly, propagated/recomputed deterministically, or marked non-applicable with evidence; unsupported or unaccounted corrections fail package generation.

The original BLS workbook digests remain immutable. The exact errata artifact is independently pinned by official identity/state and SHA-256 digest and participates, through the correction registry/coverage files, in the normalized package digest.

## Authorized implementation outcome

`official pinned BLS 4.0 XLSX inputs + pinned current official errata + authoritative typed correction registry -> deterministic normalized Food Knowledge package -> transactional/idempotent production import -> BLS-backed Base Food facts available through existing planning boundary`.

The implementation preserves:

- BLS 4.0 component codes/native units and `100 g edible portion` basis;
- all 138 component definitions;
- all six accepted evidence states without semantic collapse;
- per-value origin/reference/raw-value provenance;
- deterministic `bls:4.0:<BLS_CODE>` Base Food identity;
- explicit project-owned category mapping with exact-one classification coverage;
- immutable raw source digests plus explicit authoritative correction provenance and full errata coverage accounting.

## Remaining completion dependencies

Completion still requires:

- exact official BLS 4.0 XLSX bytes and SHA-256 digests;
- exact current official errata bytes and SHA-256 digest;
- deterministic normalized package rebuild evidence;
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
Open P1: `0` at the amended readiness level; implementation PR #11 must implement ADR-013/ADR-014 before it can leave draft.

## Next

After this canonical-routing/source-precision clarification is merged, synchronize draft PR #11 with `main` and continue only the already authorized BLS implementation slice. The XLSX boundary must preserve the published source representation before numeric coercion.
