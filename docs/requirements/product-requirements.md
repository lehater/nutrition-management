# Product Requirements

Status: `accepted`.
Lifecycle layer: `S1 Requirements`.

The system is advisory: it calculates and compares feasible purchase plans and their trade-offs rather than enforcing dietary rules.

## Household nutrition targeting

The system must support:
- a household with one or more members;
- one current profile per member;
- member inputs including age, sex, height, current weight, current-weight date, target weight, target date, physical activity and growth/development stage;
- deriving target ranges for energy, macro- and micronutrients from those inputs;
- a single MVP calculation period of 30 days;
- preserving individual member targets while aggregating them into the household target used by the MVP optimizer.

Nutrition standards must be versioned data with source/provenance. One version is active by default in the MVP.

## Food knowledge

The system must support:
- a theoretical catalog of base foods with normalized nutrient profiles;
- hierarchical food categories with stable top-level categories and extensible subcategories;
- nutrition-data provenance including at least a source name and optional URL/version/date;
- using the theoretical catalog to suggest foods that could close nutrient gaps when the purchasable catalog is insufficient.

## Purchasable catalog and offers

The system must support:
- a concrete product/SKU based on a base food;
- product-specific nutrient overrides over base-food defaults;
- real package size/quantity;
- multiple merchant offers for the same SKU;
- offer price, merchant/store and material fulfilment conditions;
- delivery cost and minimum-order conditions when applicable.

Product and offer data may be entered manually or imported. Automatic acquisition from external services is not required for the MVP.

## Purchase planning and optimization

For the 30-day household target, the system must:
- select products that reasonably cover energy, macro- and micronutrient target ranges;
- consider product categories and diet variety rather than satisfying needs from a single cheapest source;
- consider nutritionally substitutable alternatives;
- choose concrete SKUs and offers globally across the whole basket rather than optimizing each line independently;
- calculate purchasable package counts and include unavoidable package surplus in plan cost;
- include delivery-related costs and merchant minimum-order conditions in total acquisition cost;
- prefer fewer stores/purchase groups when alternatives are otherwise equivalent or close in value;
- produce the resulting purchase list with product, package quantity, merchant, selected offer price and total cost;
- report nutritional coverage and material deviations/gaps;
- report a budget estimate for the resulting nutritionally reasonable household plan.

The optimizer balances nutritional coverage, energy fit, variety, total acquisition cost and procurement simplicity. These are evaluation dimensions rather than universal hard constraints.

## MVP scope boundaries

The MVP does not require:
- medical or therapeutic diet handling;
- allergies or intolerances;
- actual consumption tracking or calorie-tracker workflows;
- per-member allocation of purchased food or proof of individual allocation feasibility;
- household inventory, carry-over stock or leftovers;
- meal, recipe, cooking, portioning or storage planning;
- nutrient-loss modeling caused by cooking/preparation;
- transport/travel cost between stores;
- multiple saved scenarios/profiles per member.
