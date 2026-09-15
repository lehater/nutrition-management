# Purchase Planning

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own the decision about which concrete 30-day household basket to recommend given nutritional demand, food knowledge and real commercial offers.

## Inputs

Purchase Planning consumes:
- the aggregated Household Nutrition Target from Nutrition Targeting;
- Base Foods, nutrient profiles and category semantics from Food Knowledge;
- Product Cards/SKUs, effective nutrient profiles, package sizes, Merchants and Offers from Market Catalog.

Provider-owned facts remain authoritative in their source contexts.

## Purchase Plan

The primary output is a recommended 30-day Purchase Plan containing:
- selected Product Cards/SKUs;
- package counts;
- selected Offers and Merchants;
- line costs and total acquisition cost;
- delivery-related costs and material order conditions;
- nutritional coverage/deviation assessment for the household target;
- variety/category assessment;
- material unresolved nutrient gaps;
- theoretical Base Food suggestions when the purchasable catalog cannot reasonably close a gap.

## Optimization semantics

The optimizer evaluates the basket globally rather than selecting the cheapest Offer for each line independently.

Evaluation dimensions include:
- nutritional coverage against target ranges;
- energy fit;
- dietary variety and category balance;
- total acquisition cost, including unavoidable package surplus and applicable delivery costs;
- procurement simplicity, including a preference for fewer merchants/purchase groups when alternatives are otherwise equivalent or close.

These dimensions are advisory trade-off criteria, not universal hard constraints.

The system may expose multiple reasonable alternatives when materially different trade-offs exist.

## Household aggregation decision

For the MVP, optimization uses the aggregated Household Nutrition Target. The optimizer does not prove that the resulting foods can be allocated to individual members such that every member independently lands inside every target range.

Individual Member Nutrition Targets remain preserved upstream for later extension and explanation.

## Invariants

- actual purchasable package counts determine cost;
- unavoidable package surplus contributes to purchase cost but does not create inventory state in the MVP;
- a Purchase Plan can select only concrete Product Cards/Offers from Market Catalog;
- theoretical Base Foods without a Product Card may be suggested as catalog gaps but cannot appear as executable purchase lines;
- Offer selection is basket-global because delivery/minimum-order conditions can couple multiple lines;
- actual consumption is not required to validate a Purchase Plan.

## Explicit exclusions

The MVP does not own actual consumption, member-level food allocation, inventory carry-over, recipes/meals, preparation, storage, medical diets/allergies or transport/travel cost between merchants.

## Material unknowns before architecture

- exact optimization/scoring model and tie-breaking policy;
- concrete variety/category rules and thresholds;
- definition of "close in value" for preferring fewer merchants;
- exact representation of infeasible plans and partial nutritional coverage;
- whether the first implementation emits one recommended plan or a Pareto-like shortlist of alternatives.
