# Food Knowledge

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own normalized nutritional knowledge about foods independently of whether a concrete commercial product is currently sold.

## Authoritative state

### Base Food

A normalized theoretical food identity used as the nutritional base for commercial Product Cards.

A Base Food owns:
- normalized nutrient profile;
- food-category membership;
- nutrition-data provenance.

The theoretical catalog may contain foods for which no purchasable Product Card currently exists.

### Nutrient Profile

Normalized energy, macro- and micronutrient values expressed in the catalog's canonical measurement basis.

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
- version and/or publication/update date when available.

## Domain operations

- normalize source nutrient data into the canonical nutrient profile;
- classify a Base Food into the food-category hierarchy;
- identify theoretical food alternatives that are relevant to an observed nutrient gap.

## Relationship to Market Catalog

A commercial Product Card references a Base Food as its semantic default. Market Catalog may provide product-specific nutrient overrides without modifying Base Food truth.

## Invariants

- Base Food identity is independent of merchant, package and price;
- nutritional provenance is retained with normalized data;
- commercial availability does not determine whether a Base Food exists;
- food-category semantics are not inferred from store taxonomy.

## MVP data acquisition

Base-food data may be entered manually or imported/prepared externally, including with agent assistance. Automatic online synchronization is not required.

## Material unknowns before architecture

- the initial controlled top-level category list;
- canonical nutrient measurement basis and rounding policy;
- exact rules for ranking theoretical alternatives for a nutrient gap.
