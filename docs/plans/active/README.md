# Active execution

Current product work: MVP domain semantics are converged; the next lifecycle step is S3 Architecture.

Lifecycle stage: `S2 Domain Design`.
Stage state: `PASS`.
Implementation authorization: `none`.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`; see [`../../problem.md`](../../problem.md).
- S1 Requirements: `PASS`; see [`../../requirements/product-requirements.md`](../../requirements/product-requirements.md).
- S2 Strategic DDD: `PASS` for the MVP scope; see [`../../domain/strategic-model.md`](../../domain/strategic-model.md) and [`../../domain/context-map.md`](../../domain/context-map.md).
- S2 Tactical DDD: `PASS` for the accepted MVP scope; see the tactical owners under `docs/domain/` and ADR-002 through ADR-007.
- accepted Bounded Contexts: `Nutrition Targeting`, `Food Knowledge`, `Market Catalog`, `Purchase Planning`.
- no target architecture is accepted yet.

## Accepted S2 decisions relevant to architecture

- ADR-002: Purchase Planning optimizes aggregated household demand while member targets remain upstream evidence; no member-allocation guarantee.
- ADR-003: active Nutrition Standard Set is `mvp-v1`; DGE/ÖGE reference semantics, DGE/Henry/PAL energy derivation and adult NIDDK/Hall weight-goal policy are fixed/versioned.
- ADR-004: BLS 4.0 component semantics and `100 g edible portion` are the canonical Food Knowledge nutrition vocabulary/basis; target-to-food comparison requires explicit mappings.
- ADR-005: controlled DGE-aligned top-level Food Categories plus `other_or_composite`; variety uses planned-quantity material representation rather than adult portion quotas.
- ADR-006: commercial model is Merchant -> Fulfilment Channel -> Offer; order-level conditions belong to the channel and temporal observation/validity is explicit.
- ADR-007: Purchase Planning uses a lexicographic nutrition-first policy, planned utilized quantity distinct from purchased package quantity, bounded variety heuristics, a 5% cost-close rule and one primary MVP recommendation.

## Accepted MVP simplifications

- one 30-day Calculation Period;
- one current Nutrition Profile per Household Member;
- date of birth is the authoritative age source; age/age band are derived at target-derivation time;
- no independent development/growth-stage profile state;
- pregnancy/lactation-specific targeting is outside the MVP;
- one active Nutrition Standard Set by default: `mvp-v1`;
- no automatic pediatric target-weight energy adjustment;
- BLS 4.0 component vocabulary and per-100-g edible basis for Food Knowledge;
- executable Product Cards resolve package quantity to edible grams;
- optimizer consumes the aggregated Household Nutrition Target;
- planned utilized quantity drives nutrition/variety; package surplus drives cost but does not become nutrition or inventory;
- no proof of per-member food allocation feasibility or member-level safety from aggregate basket totals;
- one primary Purchase Plan, not a Pareto shortlist;
- no household inventory/carry-over or actual-consumption tracking;
- no recipes/meals, cooking/preparation, portioning or storage planning;
- no medical diets, allergies or intolerances;
- no travel cost, FX conversion, loyalty/personalized pricing or complex promotion engine;
- market/product data may be manual/imported; automatic external synchronization is not required.

## S2 gate

No unresolved P0/P1 Tactical DDD contradiction remains for the accepted MVP scope.

Known limitations are explicit rather than blocking:
- `mapped_complete` covers only active Nutrition References with accepted food-side mappings and is not a complete-nutrition/safety guarantee;
- member Safety Limits remain diagnostic because member allocation/consumption is outside MVP;
- DGE food-group portion guidance is not generalized from healthy adults to aggregate households;
- price observations without source expiry remain estimates with observation provenance rather than live-price guarantees.

## Next

Open S3 Architecture. Derive the smallest realization structure that preserves the accepted context ownership, rebuildable/versioned standards, canonical nutrient mappings, basket-global commercial coupling and deterministic optimization policy. Do not start implementation until S3 passes and S4 authorizes a bounded implementation slice.
