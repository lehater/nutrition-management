# Food Knowledge

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own normalized nutritional knowledge about foods independently of whether a concrete commercial product is currently sold.

Canonical nutrient identity/unit/basis semantics are defined in [`nutrient-semantics.md`](nutrient-semantics.md) and accepted by [`ADR-004`](../decisions/ADR-004-canonical-nutrient-semantics.md).

The MVP top-level food-category decision is recorded in [`ADR-005`](../decisions/ADR-005-mvp-food-category-taxonomy.md).

## Authoritative state

### Base Food

A normalized theoretical food identity used as the nutritional base for commercial Product Cards.

A Base Food owns:
- normalized nutrient profile;
- food-category membership;
- nutrition-data provenance.

The theoretical catalog may contain foods for which no purchasable Product Card currently exists.

### Nutrient Profile

A normalized set of canonical nutrient-component values expressed per `100 g edible portion`.

For the MVP:
- canonical component identity and component unit follow the BLS 4.0 vocabulary;
- energy comparison uses BLS `ENERCC` in kcal;
- equivalent/aggregate nutrients retain their explicit component/form semantics;
- derived Nutrient Measures are explicit versioned formulas over canonical components;
- a missing or trace value is not equivalent to zero.

A nutrient data point retains source/provenance at the finest available level. BLS 4.0 imports therefore retain per-component value origin/reference where available.

### Food Category

Hierarchical classification used by Purchase Planning to reason about dietary variety.

The controlled MVP top-level categories are:

1. `beverages`;
2. `fruit_and_vegetables`;
3. `legumes_nuts_seeds`;
4. `grains_cereal_products_potatoes`;
5. `oils_and_fats`;
6. `milk_and_dairy`;
7. `fish_meat_sausage_eggs`;
8. `other_or_composite`.

The first seven align with the current DGE food-circle groups at project vocabulary granularity; seeds are an explicit project extension of the legumes/nuts group. `other_or_composite` is the project fallback for foods that do not honestly belong to one DGE group or whose composition spans groups without one clear primary role.

For the MVP:
- every Base Food has exactly one primary top-level category;
- subcategories are extensible;
- category semantics belong to Food Knowledge, not to store taxonomy or the optimizer;
- DGE adult portion/orientation values are not household constraints.

`Core variety categories` are the six top-level groups other than `beverages` and `other_or_composite`.

A category or Base Food is `materially represented` when its **planned utilized quantity** in a candidate Purchase Plan contributes at least `1%` of total planned edible food mass or at least `1%` of total planned food energy. Purchased package surplus is excluded from this assessment.

This shared semantic prevents token quantities and packaging artifacts from creating artificial variety credit while allowing both low-energy/high-mass and low-mass/high-energy foods to count meaningfully.

### Nutrition Data Source

Provenance for nutritional data. It may include:
- source name;
- source URL;
- version and/or publication/update date when available;
- per-nutrient value origin/reference when available.

BLS 4.0 is the canonical MVP semantic vocabulary and preferred baseline source for normalized theoretical food composition. Other sources may be normalized into the same semantics when equivalence and basis conversion are justified.

## Domain operations

- map a source nutrient value to an accepted canonical component only when nutrient/form semantics match;
- normalize source units and food basis to the canonical component unit per 100 g edible portion;
- preserve known numeric, known-zero, trace and unknown states;
- evaluate accepted derived Nutrient Measures from canonical components when their inputs are sufficiently known;
- classify a Base Food into exactly one MVP top-level Food Category and optional subcategories;
- determine whether a category/Base Food is materially represented from planned utilized quantity;
- identify theoretical food alternatives that are relevant to an observed nutrient gap.

## Relationship to Nutrition Targeting

Nutrition Targeting publishes reference-to-composition mappings for the active standard set. Food Knowledge does not reinterpret DGE/ÖGE target names itself.

A nutrient can participate in deterministic coverage only when the target reference maps to a canonical Food Knowledge component or accepted derived Nutrient Measure.

## Relationship to Purchase Planning

Food Knowledge publishes category identity and material-representation semantics. Purchase Planning owns planned utilized quantities and the optimization policy that uses those semantics.

For the MVP, variety assessment may use:
- count of materially represented core top-level categories;
- count of materially represented distinct Base Foods, with diminishing value for additional foods;
- concentration of total planned food energy in individual Base Foods, where greater concentration is less desirable.

These are advisory variety facts. Food Knowledge does not assign optimization weights or turn DGE adult portion values into universal household requirements.

## Relationship to Market Catalog

A commercial Product Card references a Base Food as its semantic default. Market Catalog may provide product-specific nutrient overrides without modifying Base Food truth.

An override can replace a Base Food component only after it is normalized to the same component identity, canonical unit and per-100-g edible basis.

## Invariants

- Base Food identity is independent of merchant, package and price;
- canonical food composition uses the BLS 4.0 component vocabulary for the MVP;
- normalized food composition is expressed per 100 g edible portion;
- nutrient identity is not inferred from display-name equality;
- generic unit conversion never changes nutrient identity;
- missing/trace nutrient values are not silently treated as zero;
- nutritional provenance is retained with normalized data;
- every Base Food has exactly one primary MVP top-level category;
- variety material representation is based on planned utilized quantity, not purchased package surplus;
- `other_or_composite` does not count as a core variety category;
- DGE adult portion values are not household-level constraints in the MVP;
- commercial availability does not determine whether a Base Food exists;
- food-category semantics are not inferred from store taxonomy.

## Precision and rounding

Source numeric precision is retained as provenance. Semantic normalization and derived-measure evaluation do not intentionally round intermediate results. Human-facing rounding is downstream presentation policy; optimizer tolerance is Purchase Planning policy.

## MVP data acquisition

Base-food data may be entered manually or imported/prepared externally, including with agent assistance. BLS 4.0 is available as open data and is the preferred baseline for the theoretical catalog. Automatic online synchronization is not required.

## Material unknowns before architecture

None currently owned by Food Knowledge. Exact ranking of theoretical gap-closing alternatives is Purchase Planning policy rather than canonical food truth.
