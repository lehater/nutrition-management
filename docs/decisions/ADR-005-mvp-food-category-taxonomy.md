# ADR-005 — MVP food-category taxonomy follows DGE food groups without adopting adult portion quotas

Status: `accepted`.

Date: 2026-09-15.

## Context

S1 requires Purchase Planning to consider food categories and dietary variety rather than satisfying nutrition from one cheapest source. Food Knowledge therefore needs a stable top-level category vocabulary and Purchase Planning needs category semantics that can support an anti-concentration objective.

The current DGE food-based dietary guidelines provide seven recognizable food groups and explicitly encourage variety within groups. Their quantitative orientation values, however, are derived for healthy adults aged 18–65 following an omnivorous mixed diet. Nutrition Management supports households whose members may lie outside that population, and the MVP optimizer works on aggregated household nutrition rather than individual meal/consumption allocation.

Using adult portion quotas as universal household constraints would therefore claim applicability that the source itself does not provide.

## Decision

### Controlled top-level categories

The MVP Food Knowledge top-level category set is:

1. `beverages`;
2. `fruit_and_vegetables`;
3. `legumes_nuts_seeds`;
4. `grains_cereal_products_potatoes`;
5. `oils_and_fats`;
6. `milk_and_dairy`;
7. `fish_meat_sausage_eggs`;
8. `other_or_composite`.

The first seven mirror the current DGE food-circle groups at project vocabulary granularity. `other_or_composite` is a project category required to classify foods that do not honestly fit one DGE group or whose composition spans groups without one clear primary role.

Subcategories remain extensible and may split the top-level groups into more useful nutritional/culinary distinctions.

For the MVP, each Base Food has exactly one primary top-level category. This keeps category accounting deterministic. More expressive multi-category composition may be introduced later if it demonstrates product value.

### Variety semantics

Variety is an advisory Purchase Planning dimension, not a universal nutritional hard constraint.

`Core variety categories` are the six food groups other than `beverages` and `other_or_composite`.

A selected category/Base Food counts as materially represented when it contributes at least one of:

- `1%` of total edible food mass in the plan; or
- `1%` of total food energy in the plan.

This prevents token quantities from gaming the variety score while allowing both low-energy/high-mass foods and low-mass/high-energy foods to count meaningfully.

Purchase Planning evaluates variety using three facts:

- number of materially represented core top-level categories;
- number of materially represented distinct Base Foods, with diminishing benefit from additional foods;
- concentration of plan energy in individual Base Foods, where greater concentration is worse.

The exact optimization weight/trade-off for these facts belongs to Purchase Planning policy. Food Knowledge owns only category identity/classification and the material-representation semantics shared with that policy.

### DGE portion values

DGE adult portion/orientation values are not copied into the MVP as household constraints or targets. They may remain explanatory/source evidence for future population-specific policy.

## Consequences

- category semantics are based on a recognizable external food-group model rather than store taxonomy;
- the catalog remains exhaustive enough for sweets, highly processed products and mixed/composite foods through `other_or_composite`;
- variety cannot be satisfied by adding negligible quantities of many products;
- the MVP does not pretend that adult DGE food-group portions apply to children, older adults or aggregate households;
- quantitative category quotas can be added later only with an accepted applicability policy;
- Purchase Planning still needs a final optimization/scoring decision to determine how strongly variety competes with nutrition, cost and procurement simplicity.

## Alternatives considered

### Use BLS food-code groups as the top-level planning taxonomy

Rejected because BLS classification primarily organizes food-data records; the planning requirement is nutritional variety, for which the DGE food-group vocabulary is more directly meaningful.

### Adopt DGE adult portion recommendations as hard constraints

Rejected because the source population is narrower than the product household population and the MVP does not model individual consumption allocation.

### Allow arbitrary user-defined top-level categories

Rejected for MVP because a stable controlled top-level vocabulary is required for comparable optimization semantics. Extensibility remains at the subcategory level.

### Require multiple top-level categories per Base Food

Rejected for MVP because weighted multi-category classification adds complexity before demonstrated benefit. Mixed foods can use `other_or_composite` and remain nutritionally represented through their nutrient profile.

## Supersession

Supersedes: none.
Superseded by: none.
