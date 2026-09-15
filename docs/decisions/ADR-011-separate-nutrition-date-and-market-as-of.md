# ADR-011 — Planning separates nutrition derivation date from market evaluation instant

Status: `accepted`.

Date: 2026-09-15.
Lifecycle owner: `S3 Architecture / S4 implementation contract clarification`.

## Context

Implementation of the first executable planning slice exposed an ambiguity in the previously documented command shape `GeneratePurchasePlan(household_id, as_of_date)`.

Nutrition Targeting uses calendar-date semantics: chronological age, source age bands and the 30-day target are derived for a date. Market Catalog uses instant semantics: Offer and Fulfilment Channel observations and explicit `valid_from` / `valid_until` bounds are timestamps.

A date alone cannot deterministically decide whether an Offer that becomes valid or expires within that date is executable. Choosing midnight, noon or end-of-day inside implementation would introduce an unowned business/temporal rule.

## Decision

A planning request carries two explicit temporal inputs:

- `derivation_date` — calendar date used by Nutrition Targeting for chronological age, applicability and the 30-day target;
- `market_as_of` — timezone-aware UTC instant used by Market Catalog for Offer/Fulfilment validity and commercial observation provenance.

The first-slice use case is therefore:

`GeneratePurchasePlan(household_id, derivation_date, market_as_of)`.

The Planning Input Snapshot retains both values.

The coherent database read snapshot is a technical consistency mechanism and is independent from `market_as_of`: it determines which stored observations are read, while `market_as_of` determines which of those observations are semantically executable.

The returned Purchase Plan provenance includes both `derivation_date` and `market_as_of`.

`market_as_of` must be timezone-aware and normalized to UTC at the application boundary. Naive datetimes fail explicitly.

The MVP does not infer a household timezone or convert a market instant into a local nutrition date. The caller supplies `derivation_date` explicitly. A future user-facing adapter may derive these inputs from an accepted locale/timezone policy, but that behavior is not part of the first slice.

## Consequences

- intraday Offer/Channel validity has deterministic semantics;
- birthday/age applicability remains date-based rather than accidentally tied to a server timezone;
- the first implementation slice needs no arbitrary midnight/noon convention;
- repeated runs with the same two temporal inputs and provider snapshot remain deterministic;
- S1/S2 product semantics are unchanged; this clarifies the S3/S4 technical use-case contract.

## Supersession

This decision supersedes only the single-`as_of_date` command wording in `docs/plans/active/first-implementation-slice.md` and any S3 wording that treated market `as_of` instant and nutrition derivation date as one value. All other ADR-009/S4 constraints remain accepted.

Supersedes: the conflated temporal-input detail of ADR-009 / first-slice plan.
Superseded by: none.
