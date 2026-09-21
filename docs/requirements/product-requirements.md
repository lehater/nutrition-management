# Product Requirements

Status: `accepted`.
Lifecycle layer: `S1 Requirements`.

- [PR-SCOPE-001] The system is advisory: it calculates and compares feasible purchase plans and their trade-offs rather than enforcing dietary rules.

## Household nutrition targeting

The system must support:
- [PR-NT-001] a household with one or more members;
- [PR-NT-002] one current profile per member;
- [PR-NT-003] member source inputs including date of birth, sex, height, current weight, current-weight date, target weight, target date and physical activity;
- [PR-NT-004] deriving chronological age/applicable age band from date of birth at target-derivation time rather than requiring a separately entered development/growth stage;
- [PR-NT-005] deriving energy and macro-/micronutrient target specifications from those inputs while preserving source semantics for point references, bounds, ranges, relative formulas and separate safety limits;
- [PR-NT-006] a single MVP calculation period of 30 days;
- [PR-NT-007] preserving individual member targets while aggregating compatible nutritional demand into the household target used by the MVP optimizer.
- [PR-NT-008] Nutrition standards must be versioned data with source/provenance.
- [PR-NT-009] One version is active by default in the MVP.
- [PR-NT-010] Safety upper limits must remain distinguishable from desired/reference intake targets and must not be interpreted as preferred target maxima.

## Food knowledge

The system must support:
- [PR-FK-001] a theoretical catalog of base foods with normalized nutrient profiles;
- [PR-FK-002] a canonical nutrient vocabulary/basis that permits deterministic comparison with active nutrition targets;
- [PR-FK-003] preserving unknown/trace nutrient data separately from known zero values;
- [PR-FK-004] hierarchical food categories with stable top-level categories and extensible subcategories;
- [PR-FK-005] stable variety semantics that prevent negligible token quantities or package surplus from creating artificial category/food diversity;
- [PR-FK-006] nutrition-data provenance including at least a source name and optional URL/version/date, retaining nutrient-level provenance where available;
- [PR-FK-007] using the theoretical catalog to suggest foods that could close mapped nutrient gaps when the purchasable catalog is insufficient.

## Purchasable catalog and offers

The system must support:
- [PR-MC-001] a concrete product/SKU based on a base food;
- [PR-MC-002] product-specific nutrient overrides over base-food defaults only after normalization to compatible nutrient semantics/basis;
- [PR-MC-003] real package size/quantity and enough quantity semantics to resolve an executable package to edible food mass for nutrition calculation;
- [PR-MC-004] multiple merchant/fulfilment-channel offers for the same SKU;
- [PR-MC-005] pickup and delivery fulfilment contexts with shared order-level conditions;
- [PR-MC-006] offer price/currency, availability, observation time and explicit validity interval when supplied by the source;
- [PR-MC-007] delivery/fulfilment cost, free-delivery threshold and minimum-order conditions when applicable.
- [PR-MC-008] Commercial observations without explicit expiry may be used for budget estimation with their observation age/provenance preserved; the system must not imply a live-checkout price guarantee.
- [PR-MC-009] Product, channel and offer data may be entered manually or imported.
- [PR-MC-010] Automatic acquisition from external services is not required for the MVP.

## Purchase planning and optimization

For the 30-day household target, the system must:
- [PR-PP-001] select executable products/offers that reasonably cover mapped energy, macro- and micronutrient targets;
- [PR-PP-002] preserve unsupported target mappings and unknown nutrient evidence instead of reporting them as satisfied;
- [PR-PP-003] distinguish purchased edible quantity from the quantity planned for use during the 30-day period;
- [PR-PP-004] calculate nutritional coverage and variety from planned utilized quantity rather than unavoidable package surplus;
- [PR-PP-005] consider product categories and diet variety rather than satisfying needs from a single cheapest source;
- [PR-PP-006] consider nutritionally substitutable alternatives;
- [PR-PP-007] choose concrete SKUs and offers globally across the whole basket rather than optimizing each line independently;
- [PR-PP-008] calculate purchasable integer package counts and include unavoidable package surplus in plan cost without turning it into planned nutrition or inventory;
- [PR-PP-009] group lines by fulfilment channel so delivery-related costs and minimum-order conditions are applied once at the appropriate order-group level;
- [PR-PP-010] calculate total acquisition cost in one compatible currency without implicit FX conversion;
- [PR-PP-011] prefer fewer purchase groups/merchants when nutritionally/variety-equivalent alternatives are close in acquisition cost;
- [PR-PP-012] produce one primary recommended purchase plan for the MVP;
- [PR-PP-013] return the best executable partial plan with explicit gaps/uncertainty when mapped targets or variety cannot all be satisfied;
- [PR-PP-014] report mapped nutritional coverage and material deviations/gaps;
- [PR-PP-015] report unsupported coverage dimensions separately;
- [PR-PP-016] report safety-limit information only with claims justified by the aggregate/no-allocation model;
- [PR-PP-017] report a budget estimate with price/condition observation provenance;
- [PR-PP-018] suggest theoretical Base Foods for mapped positive nutrient gaps when the purchasable catalog cannot reasonably close them.
- [PR-PP-019] The optimizer balances nutritional coverage, energy fit, variety, total acquisition cost and procurement simplicity through an explicit deterministic policy rather than treating every nutrition reference as a universal hard constraint.

## MVP scope boundaries

The MVP does not require:
- [PR-NG-001] pregnancy- or lactation-specific nutrition targeting;
- [PR-NG-002] medical or therapeutic diet handling;
- [PR-NG-003] allergies or intolerances;
- [PR-NG-004] actual consumption tracking or calorie-tracker workflows;
- [PR-NG-005] per-member allocation of purchased food or proof of individual allocation feasibility;
- [PR-NG-006] household inventory, carry-over stock or leftovers;
- [PR-NG-007] meal, recipe, cooking, portioning or storage planning;
- [PR-NG-008] nutrient-loss modeling caused by cooking/preparation;
- [PR-NG-009] transport/travel cost between stores;
- [PR-NG-010] FX conversion;
- [PR-NG-011] coupons, loyalty/personalized pricing, subscriptions or complex promotion engines;
- [PR-NG-012] multiple saved scenarios/profiles per member;
- [PR-NG-013] a Pareto-style shortlist of alternative plans in the first MVP output.
