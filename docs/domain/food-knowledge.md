# Food Knowledge

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own normalized nutritional knowledge about foods independently of whether a concrete commercial product is currently sold.

Canonical nutrient identity/unit/basis semantics are defined in [`nutrient-semantics.md`](nutrient-semantics.md) and accepted by [`ADR-004`](../decisions/ADR-004-canonical-nutrient-semantics.md).

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

For the MVP:
- top-level categories are a stable controlled set;
- subcategories are extensible;
- category semantics belong to Food Knowledge, not to the optimizer.

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
- classify a Base Food into the food-category hierarchy;
- identify theoretical food alternatives that are relevant to an observed nutrient gap.

## Relationship to Nutrition Targeting

Nutrition Targeting publishes reference-to-composition mappings for the active standard set. Food Knowledge does not reinterpret DGE/ÖGE target names itself.

A nutrient can participate in deterministic coverage only when the target reference maps to a canonical Food Knowledge component or accepted derived Nutrient Measure.

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
- commercial availability does not determine whether a Base Food exists;
- food-category semantics are not inferred from store taxonomy.

## Precision and rounding

Source numeric precision is retained as provenance. Semantic normalization and derived-measure evaluation do not intentionally round intermediate results. Human-facing rounding is downstream presentation policy; optimizer tolerance is Purchase Planning policy.

## MVP data acquisition

Base-food data may be entered manually or imported/prepared externally, including with agent assistance. BLS 4.0 is available as open data and is the preferred baseline for the theoretical catalog. Automatic online synchronization is not required.

## Material unknowns before architecture

- the initial controlled top-level category list;
- exact rules for ranking theoretical alternatives for a nutrient gap.
