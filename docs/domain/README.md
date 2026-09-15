# Domain knowledge

This directory owns living Strategic and Tactical DDD for Nutrition Management.

Current state:
- Strategic DDD baseline: `accepted` for the MVP;
- Tactical DDD baseline: partially accepted and still being refined;
- target architecture: not accepted.

## Strategic model

- [`strategic-model.md`](strategic-model.md) — accepted Bounded Contexts and semantic ownership;
- [`context-map.md`](context-map.md) — material semantic relationships between contexts;
- [`glossary.md`](glossary.md) — accepted ubiquitous-language terms.

## Tactical owners

- [`nutrition-targeting.md`](nutrition-targeting.md) — household/member profiles, standards and derived nutritional targets;
- [`nutrition-standard-set-mvp-v1.md`](nutrition-standard-set-mvp-v1.md) — active sourced MVP nutrition-reference and target-derivation policy;
- [`nutrient-semantics.md`](nutrient-semantics.md) — canonical nutrient identity, unit, food-basis and target-to-food comparison semantics;
- [`food-knowledge.md`](food-knowledge.md) — Base Foods, nutrient profiles, categories and nutritional-data provenance;
- [`market-catalog.md`](market-catalog.md) — Product Cards/SKUs, nutrient overrides, Merchants and Offers;
- [`purchase-planning.md`](purchase-planning.md) — basket optimization semantics and Purchase Plan output.

The MVP household-aggregation simplification and its rationale are recorded in [`../decisions/ADR-002-mvp-household-aggregate-optimization.md`](../decisions/ADR-002-mvp-household-aggregate-optimization.md).

The active Nutrition Targeting standards/formula decision is recorded in [`../decisions/ADR-003-nutrition-targeting-standards-and-derivation.md`](../decisions/ADR-003-nutrition-targeting-standards-and-derivation.md).

The canonical nutrient-semantics decision is recorded in [`../decisions/ADR-004-canonical-nutrient-semantics.md`](../decisions/ADR-004-canonical-nutrient-semantics.md).

Do not infer domain structure from database tables, APIs, screens, packages or deployment units.
