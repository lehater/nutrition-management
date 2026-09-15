# Product Requirements

Status: `accepted`.
Lifecycle layer: `S1 Requirements`.

The system is advisory: it calculates and compares feasible purchase plans and their trade-offs rather than enforcing dietary rules.

## Household nutrition targeting

The system must support:
- a household with one or more members;
- one current profile per member;
- member source inputs including date of birth, sex, height, current weight, current-weight date, target weight, target date and physical activity;
- deriving chronological age/applicable age band from date of birth at target-derivation time rather than requiring a separately entered development/growth stage;
- deriving energy and macro-/micronutrient target specifications from those inputs while preserving source semantics for point references, bounds, ranges, relative formulas and separate safety limits;
- a single MVP calculation period of 30 days;
- preserving individual member targets while aggregating compatible nutritional demand into the household target used by the MVP optimizer.

Nutrition standards must be versioned data with source/provenance. One version is active by default in the MVP. Safety upper limits must remain distinguishable from desired/reference intake targets and must not be interpreted as preferred target maxima.

## Food knowledge

The system must support:
- a theoretical catalog of base foods with normalized nutrient profiles;
- a canonical nutrient vocabulary/basis that permits deterministic comparison with active nutrition targets;
- preserving unknown/trace nutrient data separately from known zero values;
- hierarchical food categories with stable top-level categories and extensible subcategories;
- stable variety semantics that prevent negligible token quantities from creating artificial category/food diversity;
- nutrition-data provenance including at least a source name and optional URL/version/date, retaining nutrient-level provenance where available;
- using the theoretical catalog to suggest foods that could close mapped nutrient gaps when the purchasable catalog is insufficient.

## Purchasable catalog and offers

The system must support:
- a concrete product/SKU based on a base food;
- product-specific nutrient overrides over base-food defaults only after normalization to compatible nutrient semantics/basis;
- real package size/quantity and enough quantity semantics to resolve an executable package to edible food mass for nutrition calculation;
- multiple merchant/fulfilment-channel offers for the same SKU;
- pickup and delivery fulfilment contexts with shared order-level conditions;
- offer price/currency, availability, observation time and explicit validity interval when supplied by the source;
- delivery/fulfilment cost, free-delivery threshold and minimum-order conditions when applicable.

Commercial observations without explicit expiry may be used for budget estimation with their observation age/provenance preserved; the system must not imply a live-checkout price guarantee.

Product, channel and offer data may be entered manually or imported. Automatic acquisition from external services is not required for the MVP.

## Purchase planning and optimization

For the 30-day household target, the system must:
- select executable products/offers that reasonably cover mapped energy, macro- and micronutrient targets;
- preserve unsupported target mappings and unknown nutrient evidence instead of reporting them as satisfied;
- consider product categories and diet variety rather than satisfying needs from a single cheapest source;
- consider nutritionally substitutable alternatives;
- choose concrete SKUs and offers globally across the whole basket rather than optimizing each line independently;
- calculate purchasable integer package counts and include unavoidable package surplus in plan cost/nutrient totals;
- group lines by fulfilment channel so delivery-related costs and minimum-order conditions are applied once at the appropriate order-group level;
- calculate total acquisition cost in one compatible currency without implicit FX conversion;
- prefer fewer purchase groups/merchants when nutritionally/variety-equivalent alternatives are close in acquisition cost;
- produce one primary recommended purchase plan for the MVP;
- return the best executable partial plan with explicit gaps/uncertainty when mapped targets or variety cannot all be satisfied;
- report mapped nutritional coverage and material deviations/gaps;
- report unsupported coverage dimensions separately;
- report safety-limit information only with claims justified by the aggregate/no-allocation model;
- report a budget estimate with price/condition observation provenance;
- suggest theoretical Base Foods for mapped positive nutrient gaps when the purchasable catalog cannot reasonably close them.

The optimizer balances nutritional coverage, energy fit, variety, total acquisition cost and procurement simplicity through an explicit deterministic policy rather than treating every nutrition reference as a universal hard constraint.

## MVP scope boundaries

The MVP does not require:
- pregnancy- or lactation-specific nutrition targeting;
- medical or therapeutic diet handling;
- allergies or intolerances;
- actual consumption tracking or calorie-tracker workflows;
- per-member allocation of purchased food or proof of individual allocation feasibility;
- household inventory, carry-over stock or leftovers;
- meal, recipe, cooking, portioning or storage planning;
- nutrient-loss modeling caused by cooking/preparation;
- transport/travel cost between stores;
- FX conversion;
- coupons, loyalty/personalized pricing, subscriptions or complex promotion engines;
- multiple saved scenarios/profiles per member;
- a Pareto-style shortlist of alternative plans in the first MVP output.
