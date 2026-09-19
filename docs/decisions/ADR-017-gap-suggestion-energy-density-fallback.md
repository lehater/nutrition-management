# ADR-017 — Gap suggestions rank computable nutrient density before fallback density

Status: `accepted` for the Harness pilot branch.

Date: 2026-09-19.
Lifecycle owner: `S2 Tactical Domain Design / Purchase Planning suggestion ranking`.

## Context

ADR-007 ranks theoretical Base Food suggestions for a positive mapped lower-bound or adequacy gap first by the missing Nutrient Measure per `100 kcal` when food energy is positive and known, then by the missing measure per `100 g`, variety contribution and stable Base Food identity.

Implementation review exposed one unspecified comparison: an eligible food can have a known positive amount of the missing nutrient while its `ENERCC` evidence is zero or non-quantitative. Its per-`100 kcal` density is therefore not computable.

Without an explicit rule, two implementations could order the same canonical Food Knowledge differently.

## Decision

For a non-energy nutrient gap:

1. a Base Food is eligible only when the missing Nutrient Measure is quantitatively known and strictly positive;
2. when `ENERCC` is quantitatively known and strictly positive, calculate the primary density as:

   `missing measure per 100 kcal = amount_per_100g × 100 / ENERCC_per_100g`;

3. foods with a computable per-`100 kcal` density rank before foods for which that primary density is unavailable;
4. among foods with computable primary density, higher density ranks first;
5. within the remaining tie or fallback class, higher missing-measure amount per `100 g` ranks first;
6. then prefer a core category not materially represented in the current Purchase Plan;
7. stable Base Food identity is the final deterministic tie-breaker.

A missing, trace, limit-qualified, or zero energy value does not become an invented numeric denominator and does not receive an implicit infinite/zero density score.

For an energy gap itself, `ENERCC` must be known and strictly positive by eligibility, and ranking uses higher `ENERCC` per `100 g` directly as already required by ADR-007.

## Consequences

- ranking is deterministic even when Food Knowledge lacks quantitative energy for an otherwise eligible food;
- missing energy evidence is not converted into false precision;
- foods with incomplete energy evidence remain eligible as fallback suggestions rather than being silently discarded;
- the accepted ADR-007 ordering remains intact: per-`100 kcal` density is primary where it can actually be calculated, then per-`100 g`, variety contribution and stable identity;
- no change is made to executable basket selection or Purchase Plan outcome semantics.

## Alternatives considered

### Exclude foods whose energy is unavailable

Rejected because ADR-007 eligibility is based on a known positive amount of the missing Nutrient Measure, not on complete energy evidence.

### Treat unavailable per-100-kcal density as zero

Rejected because zero would be a fabricated quantitative score.

### Compare every food only by per-100-g amount when any candidate lacks energy

Rejected because it would discard the accepted primary per-`100 kcal` ranking for candidates where that metric is valid.

## Supersession

Supersedes: none.
Superseded by: none.
