# BLS 4.0 Food Knowledge slice — semantic amendment

Status: `PASS` — S4 amendment after source inspection.
Lifecycle owner: Food Knowledge / S4 Implementation Readiness.

This amendment is read together with [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md). Where the original readiness plan describes a four-state `missing / trace / zero / known` evidence model or literal import of the pinned workbook, ADR-013 and ADR-014 are authoritative.

## Trigger

Implementation-time inspection of the official BLS 4.0 documentation exposed two source facts that were not represented in the original readiness packet:

1. BLS distinguishes `<LOQ` and `<LOD` from both `Spuren` (`TR`) and missing values.
2. MRI maintains a BLS 4.0 errata document. The current authoritative state is `August 2026`, broader than the earlier February milk-only correction, and contains direct as well as calculation/propagation corrections that apply before the next BLS update.

The original readiness plan explicitly required an S2 stop when source inspection revealed semantics that could not be represented without weakening accepted meanings. ADR-013 and ADR-014 resolve that stop.

## Amended evidence contract

Normalized Food Knowledge evidence states are:

- `known`;
- `zero`;
- `trace`;
- `below_quantification_limit`;
- `below_detection_limit`;
- `missing`.

Only `known` and `zero` carry deterministic numeric amounts. The other four states remain distinct provenance/evidence claims but do not contribute a numeric amount to deterministic Purchase Planning arithmetic.

The BLS normalizer accepts exactly the thirteen documented BLS 4.0 data-origin categories and fails closed on an unexpected non-empty origin.

Parser/regression evidence must cover at least:

- positive numeric known value;
- logical zero;
- computed/non-logical numeric zero;
- `Spuren` / `TR`;
- `<LOQ`;
- `<LOD`;
- missing value;
- negative/inconsistent source-cell rejection;
- unknown data-origin rejection.

## Amended source-correction contract

The deterministic normalized package adds two source-governance artifacts to its manifest inventory:

- a versioned typed correction registry;
- errata coverage accounting proving that every correction family in the pinned current official BLS 4.0 errata is applied, propagated/recomputed, or explicitly non-applicable.

The exact official errata artifact is pinned by publication state/date, official locator and SHA-256 digest. The original workbook digests remain unchanged.

The correction model must support more than direct cell replacement. Package generation must be able to represent direct value/qualifier corrections, source-origin/reference corrections and corrections whose effects propagate through formulas, recipes or other derived BLS values. Unsupported correction types reject generation instead of being silently skipped.

The previously published `M111100` RETOL/VITA/VITAA correction remains a required regression case, but it is not the completeness boundary; **the current August 2026 errata as a whole is**.

## Downstream implementation impact

The implementation slice must additionally update:

- Food Knowledge evidence enums/invariants and persistence validation;
- published Food Knowledge application contracts;
- Market Catalog projection preservation of non-quantitative evidence states;
- Purchase Planning evidence handling so every state other than `known`/`zero` is quantitatively unavailable;
- reporting/regression tests for the extended state set;
- package manifest validation for the correction registry, pinned errata identity and coverage accounting;
- source-normalization tooling so correction propagation is deterministic and fail-closed.

No optimizer objective or nutrition-target policy changes are authorized.

## Readiness result

S2: `PASS` after ADR-013 and ADR-014.
S3: `PASS`; no architecture change is required.
S4: `PASS` as amended.

Open P0: `0`.
Open P1: `0` after the amendment is implemented before production-package completion.

The exact official XLSX bytes/digests, exact current errata bytes/digest and full 7,140-food category registry remain completion dependencies.
