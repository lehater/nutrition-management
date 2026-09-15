# Active execution

Current product work: tactical domain discovery for the MVP.

Lifecycle stage: `S2 Domain Semantics / Tactical DDD`.
Stage state: `IN_PROGRESS`.
Implementation authorization: `none`.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`; see [`../../problem.md`](../../problem.md).
- S1 Requirements: `PASS`; see [`../../requirements/product-requirements.md`](../../requirements/product-requirements.md).
- S2 Strategic DDD: `PASS` for the MVP scope; see [`../../domain/strategic-model.md`](../../domain/strategic-model.md) and [`../../domain/context-map.md`](../../domain/context-map.md).
- accepted Bounded Contexts: `Nutrition Targeting`, `Food Knowledge`, `Market Catalog`, `Purchase Planning`.
- no target architecture is accepted yet.

## Current objective

Define the minimum tactical semantics required for the first end-to-end calculation without designing persistence, APIs or framework structure.

Priority order:
1. Nutrition Targeting identities, inputs, standards and target calculation semantics;
2. Food Knowledge base-food/category/nutrient semantics;
3. Market Catalog SKU/offer semantics and effective nutrient data;
4. Purchase Planning optimization inputs, outputs and invariants.

## Deferred MVP concerns

Per-member food allocation feasibility, inventory, actual consumption, recipes/meals, cooking/preparation, portioning, storage, medical diets/allergies, transport cost and automatic external catalog/price acquisition are outside the current tactical slice.
