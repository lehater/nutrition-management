# ADR-002 — MVP optimization uses aggregated household nutrition demand

Status: `accepted`.

Date: 2026-09-15.

## Context

Nutrition Management derives nutritional needs per household member, but the first end-to-end product goal is to calculate a practical household purchase basket and its cost. Proving that every selected food quantity can be allocated among members while each member independently satisfies every target range would add a materially larger optimization problem and implicitly introduce consumption/allocation semantics that are otherwise outside the MVP.

## Decision

The MVP preserves Member Nutrition Targets but aggregates them into one 30-day Household Nutrition Target for Purchase Planning.

Purchase Planning optimizes the household basket against this aggregate target and does not prove per-member allocation feasibility.

## Consequences

- The first optimizer remains materially simpler and aligned with the purchase-only MVP.
- Individual nutritional derivation remains available and is not lost in aggregation.
- A nutritionally adequate aggregate basket is not proof that every household member can be allocated food so that all of their individual ranges are satisfied.
- Product output must not claim such a guarantee.
- The model remains extensible because Member Nutrition Targets are retained upstream.

Revisit this decision when the product requires strict individual diets, member-level meal/allocation planning, actual consumption tracking or guarantees of individual target satisfaction.

## Alternatives considered

### Optimize per member from the first version

Rejected for MVP because it increases optimization dimensionality and requires semantics for allocating shared purchased food among people before allocation/consumption is a product requirement.

### Aggregate needs and discard individual targets

Rejected because it would lose useful provenance and make later individual allocation or explanation unnecessarily difficult.

## Supersession

Supersedes: none.
Superseded by: none.
