# Nutrition Management Strategic DDD model

Status: `accepted`.
Lifecycle layer: `S2 Domain Semantics / Strategic DDD`.

## Domain

Nutrition Management organizes household food purchasing against nutritional needs, market availability and acquisition cost.

## Subdomains and Bounded Contexts

### Nutrition Targeting

Purpose: derive the nutritional target that purchase planning must satisfy.

Owns:
- household membership for calculation purposes;
- member nutrition profile;
- versioned nutrition standard sets and their provenance;
- derivation of individual 30-day energy/nutrient target specifications and applicable safety limits;
- aggregation of compatible nutritional demand into the household 30-day nutrition target.

Does not own food composition, products, prices or purchase decisions.

### Food Knowledge

Purpose: provide normalized food knowledge independently of what is currently sold.

Owns:
- base food identity;
- normalized nutrient profile;
- hierarchical food categories;
- food/nutrition-data provenance;
- theoretical food alternatives relevant to nutrient gaps.

Does not own concrete commercial products, merchants or prices.

### Market Catalog

Purpose: represent what can actually be purchased and under which commercial conditions.

Owns:
- concrete product/SKU identity;
- relationship from an SKU to its base food;
- SKU-specific nutrient overrides;
- package size/quantity;
- merchant/store identity needed by purchasing;
- offers and their prices;
- delivery/minimum-order and other material fulfilment conditions.

A concrete SKU may have multiple offers from different merchants.

### Purchase Planning

Purpose: produce a practical 30-day household purchase plan by balancing nutritional coverage, variety, acquisition cost and procurement simplicity.

Owns:
- household-level optimization policy;
- candidate basket evaluation;
- selection of concrete SKUs and offers;
- package quantities;
- selected merchant grouping;
- purchase-plan total cost;
- nutritional coverage/deviation assessment for the resulting household basket;
- gap reporting and requests for theoretical alternatives when the purchasable catalog is insufficient.

The MVP optimizer operates on the aggregated household nutrition target. Per-member allocation feasibility is explicitly deferred.

## Strategic classification

- Core: `Purchase Planning` — combines nutritional and market semantics to produce the product's primary decision output.
- Supporting: `Nutrition Targeting`, `Market Catalog`.
- Generic/supporting knowledge: `Food Knowledge`; much of its source data may come from external datasets, but normalized project semantics remain owned here.

## Explicit MVP exclusions

No accepted Bounded Context is introduced yet for inventory, consumption tracking, recipes/meals, cooking, preparation, portioning, storage or medical diet management.

Bounded Contexts are semantic ownership boundaries only; this model makes no decision about services, databases, packages or deployment units.
