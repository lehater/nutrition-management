# Domain knowledge

This directory owns living Strategic and Tactical DDD for Nutrition Management.

Current state:
- Strategic DDD baseline: `accepted` for the MVP;
- Tactical DDD baseline: `accepted` for the MVP;
- target architecture: not accepted.

## Strategic model

- [`strategic-model.md`](strategic-model.md) — accepted Bounded Contexts and semantic ownership;
- [`context-map.md`](context-map.md) — material semantic relationships between contexts;
- [`glossary.md`](glossary.md) — accepted ubiquitous-language terms.

## Tactical owners

- [`nutrition-targeting.md`](nutrition-targeting.md) — household/member profiles, standards and derived nutritional targets;
- [`nutrition-standard-set-mvp-v1.md`](nutrition-standard-set-mvp-v1.md) — active sourced MVP nutrition-reference and target-derivation policy;
- [`nutrient-semantics.md`](nutrient-semantics.md) — canonical nutrient identity, unit, food-basis and target-to-food comparison semantics;
- [`food-knowledge.md`](food-knowledge.md) — Base Foods, canonical nutrient profiles, categories and nutritional-data provenance;
- [`market-catalog.md`](market-catalog.md) — Product Cards/SKUs, edible package quantities, Merchants, Fulfilment Channels and Offers;
- [`purchase-planning.md`](purchase-planning.md) — executable basket optimization semantics and Purchase Plan output.

## Consequential S2 decisions

- [`ADR-002`](../decisions/ADR-002-mvp-household-aggregate-optimization.md) — MVP optimizes the aggregated household target while preserving member targets upstream;
- [`ADR-003`](../decisions/ADR-003-nutrition-targeting-standards-and-derivation.md) — active Nutrition Standard Set, applicability and target-derivation policy;
- [`ADR-004`](../decisions/ADR-004-canonical-nutrient-semantics.md) — canonical BLS-based nutrient semantics and target-to-food mappings;
- [`ADR-005`](../decisions/ADR-005-mvp-food-category-taxonomy.md) — controlled food-category taxonomy and shared variety facts;
- [`ADR-006`](../decisions/ADR-006-market-offer-and-fulfilment-semantics.md) — Merchant/Fulfilment Channel/Offer commercial semantics;
- [`ADR-007`](../decisions/ADR-007-mvp-purchase-optimization-policy.md) — deterministic MVP purchase-optimization and outcome policy.

Do not infer domain structure from database tables, APIs, screens, packages or deployment units.
