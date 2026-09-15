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
- semantic mapping from active nutrient references to food-side Nutrient Measures;
- aggregation of compatible nutritional demand into the household 30-day nutrition target.

Does not own food composition, products, prices or purchase decisions.

### Food Knowledge

Purpose: provide normalized food knowledge independently of what is currently sold.

Owns:
- base food identity;
- canonical BLS-based nutrient-component vocabulary and normalized nutrient profiles;
- derived food-side Nutrient Measures;
- hierarchical food categories and shared material-representation semantics for variety;
- food/nutrition-data provenance;
- theoretical food alternatives relevant to nutrient gaps.

Does not own concrete commercial products, merchants or prices.

### Market Catalog

Purpose: represent what can actually be purchased and under which commercial conditions.

Owns:
- concrete product/SKU identity;
- relationship from an SKU to its base food;
- SKU-specific nutrient overrides;
- package size and edible-quantity conversion required for quantitative nutrition calculation;
- Merchant identity;
- Fulfilment Channels and their order-level conditions;
- Offers, availability, observed prices/currencies and explicit validity semantics.

A concrete SKU may have multiple Offers across Merchants/Fulfilment Channels.

### Purchase Planning

Purpose: produce a practical 30-day household purchase plan by balancing mapped nutritional coverage, variety, acquisition cost and procurement simplicity.

Owns:
- household-level optimization policy;
- candidate basket executability/evaluation;
- selection of concrete SKUs and Offers;
- integer package quantities;
- Purchase Groups formed from Fulfilment Channels;
- purchase-plan total cost;
- mapped nutritional coverage/deviation and uncertainty assessment;
- variety assessment;
- gap reporting and requests for theoretical alternatives when the purchasable catalog is insufficient.

The MVP optimizer operates on the aggregated household nutrition target. Per-member allocation feasibility and individual safety guarantees are explicitly deferred.

## Strategic classification

- Core: `Purchase Planning` — combines nutritional and market semantics to produce the product's primary decision output.
- Supporting: `Nutrition Targeting`, `Market Catalog`.
- Generic/supporting knowledge: `Food Knowledge`; much of its source data may come from external datasets, but normalized project semantics remain owned here.

## Explicit MVP exclusions

No accepted Bounded Context is introduced for inventory, consumption tracking, recipes/meals, cooking, preparation, portioning, storage or medical diet management.

Bounded Contexts are semantic ownership boundaries only; this model makes no decision about services, databases, packages or deployment units.
