# Purchase Planning

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own the decision about which concrete 30-day household basket to recommend given nutritional demand, food knowledge and executable commercial offers.

The MVP optimization policy is accepted by [`ADR-007`](../decisions/ADR-007-mvp-purchase-optimization-policy.md).

## Inputs

Purchase Planning consumes:
- the aggregated Household Nutrition Target from Nutrition Targeting, preserving source target semantics and provenance;
- Base Foods, canonical nutrient profiles, Nutrient Measures and category/variety semantics from Food Knowledge;
- executable Product Cards/SKUs, effective nutrient profiles, edible package quantities, Merchants, Fulfilment Channels and Offers from Market Catalog.

Provider-owned facts remain authoritative in their source contexts.

## Purchase Plan

The MVP produces one primary recommended Purchase Plan containing:
- selected Product Cards/SKUs;
- integer package counts;
- selected Offers, Fulfilment Channels and Merchants;
- Purchase Groups formed by Fulfilment Channel;
- line costs, group-level fulfilment/delivery costs and total acquisition cost;
- price/condition observation provenance;
- mapped nutritional coverage/deviation assessment;
- unsupported target mappings and indeterminate nutrient evidence;
- member-level safety-limit diagnostics where a compatible comparison signal exists, without claiming individual safety;
- variety/category assessment;
- outcome: `mapped_complete`, `partial`, or `no_executable_plan`;
- material mapped nutrient gaps;
- theoretical Base Food suggestions for mapped positive adequacy gaps when the purchasable catalog cannot close them.

`mapped_complete` means complete only against active target references that have accepted food-side mappings. It is not a claim of complete nutrition, member-level adequacy, safety or actual consumption adequacy.

## Executability

A candidate basket is executable only when:
- package counts are non-negative integers;
- each selected Product Card resolves package quantity to edible grams;
- each selected Offer is `available` and inside explicit validity bounds when present;
- each selected Fulfilment Channel is inside explicit condition validity bounds when present;
- all selected monetary values use one compatible currency;
- every used Purchase Group satisfies its channel minimum-order condition;
- channel fulfilment/delivery fees are applied exactly once per Purchase Group.

A non-executable catalog item may still exist upstream but cannot appear as an executable Purchase Plan line.

## Target evaluation

Purchase Planning evaluates only accepted target-to-food Nutrient Measure mappings.

Known numeric and known-zero food values provide exact arithmetic evidence. Trace/unknown values remain uncertainty.

For mapped target kinds:
- recommended-intake and estimated-value points are adequacy floors;
- lower-bound guidelines penalize shortfall;
- upper-bound guidelines penalize excess;
- interval guidelines penalize distance outside the source interval;
- point guidelines use an optimizer-only `±5%` zero-penalty tolerance;
- household energy uses the same `±5%` point tolerance.

Purchase Planning never rewrites the upstream Nutrition Reference. Its tolerance is downstream scoring policy only.

For lower-bound evidence, known contributions can prove a minimum even when some selected foods have unknown values for that nutrient; the unknown contribution is still flagged. For upper-bound, interval and point assessments, selected-food unknown contribution makes the assessment `indeterminate` because compliance cannot be proven.

Unmapped active Nutrition References are reported as `unsupported coverage` and are never silently treated as satisfied or zero.

## Safety semantics

Member Safety Limits do not become household hard constraints in the MVP.

Where compatible member-level data permits an aggregate comparison signal, Purchase Planning may report a diagnostic warning. The signal does not prove that any member will or will not exceed a Safety Limit because the MVP does not model allocation or actual consumption.

## Nutritional ranking

Executable candidates are ranked lexicographically by:

1. fewer indeterminate mapped target assessments;
2. lower maximum normalized directed-target violation;
3. lower mean normalized directed-target violation;
4. lower maximum point-guideline/energy penalty;
5. lower mean point-guideline/energy penalty.

Adequately satisfied dimensions receive no extra benefit from unlimited oversupply.

This keeps nutritional adequacy ahead of price while avoiding a weighted sum that mixes euros with nutrient percentages.

## Variety semantics

Variety uses ADR-005 material representation: a Base Food/category counts when it contributes at least `1%` of total edible mass or `1%` of total food energy.

The MVP variety target is:
- at least `4` of `6` core top-level Food Categories materially represented;
- at least `8` distinct Base Foods materially represented;
- no single Base Food above `25%` of total plan food energy.

These are product heuristics, not medical or DGE population requirements.

Once all three conditions are met, extra variety does not outrank cost. If they cannot all be met, prefer in order: category count capped at 4, Base Food count capped at 8, then lower single-food energy concentration down to 25%.

## Cost and procurement simplicity

After nutritional quality and variety are optimized:

`total acquisition cost = package line costs + applicable Purchase Group fulfilment/delivery fees`.

Unavoidable whole-package surplus contributes to purchased nutrient quantities and cost but creates no inventory state.

Let `Cmin` be the lowest cost among candidates tied on the preceding nutrition/variety policy. Candidates costing no more than `1.05 × Cmin` are `cost-close`.

Among cost-close candidates prefer:
1. fewer Purchase Groups;
2. fewer distinct Merchants;
3. lower total acquisition cost;
4. lower total edible package surplus mass.

The MVP therefore allows up to a 5% premium over the cheapest nutrition/variety-equivalent basket when that materially simplifies procurement.

## Outcome semantics

- `mapped_complete` — every mapped active target is determinate and has zero nutrition/energy penalty, and the variety target is met;
- `partial` — an executable basket exists but at least one mapped target is violated/indeterminate or variety cannot be met;
- `no_executable_plan` — no non-empty basket can be built from executable Offers under current market constraints.

A `partial` plan is still returned as the best available result and must expose its gaps/uncertainty.

Unsupported active target mappings are always shown separately, including for a `mapped_complete` result.

## Gap-closing theoretical suggestions

For a positive mapped adequacy gap, theoretical Base Foods with a known positive amount of the missing Nutrient Measure are ranked by:
1. higher amount per `100 kcal`, when energy is positive and known;
2. higher amount per `100 g edible portion`;
3. a core category not already materially represented;
4. stable Base Food identity.

For an energy gap, rank by `ENERCC` per `100 g` instead of the trivial per-100-kcal measure.

A Base Food without an executable Product Card/Offer remains only a theoretical suggestion.

## Invariants

- actual integer package counts determine purchased quantities and line cost;
- Purchase Group conditions/fees are evaluated once per Fulfilment Channel;
- unavoidable package surplus contributes to cost and nutrient totals but does not create inventory state;
- a Purchase Plan selects only executable Product Cards/Offers;
- theoretical Base Foods without executable Offers cannot appear as purchase lines;
- target semantic kind supplied by Nutrition Targeting is not reinterpreted;
- unsupported and indeterminate nutrient dimensions remain visible;
- member safety is never inferred from aggregate basket totals;
- actual consumption is not required to calculate a Purchase Plan and is not claimed by it.

## Explicit exclusions

The MVP does not own actual consumption, member-level food allocation, inventory carry-over, recipes/meals, preparation, storage, medical diets/allergies, travel cost, FX conversion, coupons/loyalty pricing or complex promotion engines.

## Material unknowns before architecture

None currently owned by Purchase Planning for the accepted MVP scope.
