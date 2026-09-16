# BLS 4.0 Food Knowledge slice — semantic amendment

Status: `PASS` — S4 amendment after source inspection.
Lifecycle owner: Food Knowledge / S4 Implementation Readiness.

This amendment is read together with [`bls-v4-food-knowledge-slice.md`](bls-v4-food-knowledge-slice.md). Where the original readiness plan describes a four-state `missing / trace / zero / known` evidence model or literal import of the pinned workbook, ADR-012 and ADR-013 are authoritative.

## Trigger

Implementation-time inspection of the official BLS 4.0 documentation exposed two source facts that were not represented in the original readiness packet:

1. BLS distinguishes `<LOQ` and `<LOD` from both `Spuren` (`TR`) and missing values.
2. MRI published a February 2026 erratum requiring corrected values for BLS food `M111100` until a later BLS update incorporates the fix.

The original readiness plan explicitly required an S2 stop when source inspection revealed semantics that could not be represented without weakening accepted meanings. ADR-012 and ADR-013 resolve that stop.

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

The deterministic normalized package adds a versioned correction-registry file to its manifest inventory.

For BLS 4.0 it must contain and apply the official MRI February 2026 erratum for `M111100`:

- `RETOL = 2.4 µg/100 g`;
- `VITA = 3.1 µg/100 g`;
- `VITAA = 2.7 µg/100 g`.

The original workbook digests remain unchanged. The correction registry records the authoritative erratum locator and enough original-versus-corrected provenance for audit. The package digest covers the correction registry.

## Downstream implementation impact

The implementation slice must additionally update:

- Food Knowledge evidence enums/invariants and persistence validation;
- published Food Knowledge application contracts;
- Market Catalog projection preservation of non-quantitative evidence states;
- Purchase Planning evidence handling so every state other than `known`/`zero` is quantitatively unavailable;
- reporting/regression tests for the extended state set;
- package manifest validation for the source-correction registry.

No optimizer objective or nutrition-target policy changes are authorized.

## Readiness result

S2: `PASS` after ADR-012 and ADR-013.
S3: `PASS`; no architecture change is required.
S4: `PASS` as amended.

Open P0: `0`.
Open P1: `0` after the amendment is implemented before production-package completion.

The exact official XLSX bytes/digests and full 7,140-food category registry remain completion dependencies exactly as before.
