# Active execution

Current product work: implement the authorized BLS 4.0 Food Knowledge source-data/import slice.

Lifecycle state: **Implementation IN_PROGRESS** under accepted S2/S3/S4 gates.
Implementation authorization: **only** [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md).
Implementation base: `f1f8e0f06bc46c493f1ad73998e68741f7c0c2bb` (PR #10 squash merge).

## Accepted upstream state

- S0 Problem / Evidence: `PASS`.
- S1 Requirements: `PASS`.
- S2 Strategic/Tactical Domain Design: `PASS`; ADR-004 makes BLS 4.0 the canonical MVP food-composition vocabulary and ADR-005 owns the project food-category taxonomy.
- S3 Architecture: `PASS`; existing modular monolith, Food Knowledge ownership and one relational store remain valid.
- S4 Implementation Readiness: `PASS` for the bounded BLS 4.0 Food Knowledge source-data/import slice.
- Previous `mvp-v1` Nutrition Standard Set slice: completion gate `PASS`, squash-merged as commit `93b44914913ec9b8bdfdfd69d9bd48cc2fefaf4a` via PR #9.

## Authorized implementation

Canonical readiness plan: [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md).

Implement:

`official pinned BLS 4.0 XLSX inputs -> deterministic normalized Food Knowledge package -> transactional/idempotent production import -> BLS-backed Base Food facts available through existing planning boundary`.

The first executable increment is structural: extend Food Knowledge persistence/package validation for BLS component vocabulary and per-value provenance while keeping the published planning facts minimal. Then add source normalization and the complete pinned corpus.

## Required completion evidence

Before this slice may be called complete:

- exact official BLS 4.0 source file digests and CC BY 4.0 attribution are recorded;
- normalized package rebuild is deterministic and byte-reproducible;
- package contains the pinned 7,140 foods and 138 component definitions;
- every food resolves to exactly one ADR-005 top-level category without name-based inference;
- missing / trace / zero / known evidence and per-value origin/reference provenance round-trip correctly;
- migrations work from the current schema and an empty database;
- import is transactional, identical-content idempotent and rejects conflicting same-version content;
- representative BLS foods flow through `FoodKnowledgeRepository` and the Planning Snapshot boundary;
- existing target, solver, architecture-boundary and first-slice regressions remain green.

## Current execution constraint

The repository implementation can proceed with structural package/import/persistence work using deterministic fixtures. Completion remains blocked until the exact official BLS 4.0 XLSX bytes are available to pin SHA-256 source digests and generate/review the complete normalized production package. No digest or source corpus will be fabricated.

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
Open P1: `0` at implementation start.

## Next

Implement the source-rich Food Knowledge persistence and deterministic normalized-package validator/importer first, with regression tests. Keep the implementation PR draft until the full official source/corpus completion gate passes.