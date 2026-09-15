# Active execution

Current product work: complete the MVP tactical domain model and close material unknowns before architecture.

Lifecycle stage: `S2 Domain Semantics / Tactical DDD`.
Stage state: `IN_PROGRESS`.
Implementation authorization: `none`.

## Accepted upstream state

- S0 Problem / Evidence: `PASS`; see [`../../problem.md`](../../problem.md).
- S1 Requirements: `PASS`; see [`../../requirements/product-requirements.md`](../../requirements/product-requirements.md).
- S2 Strategic DDD: `PASS` for the MVP scope; see [`../../domain/strategic-model.md`](../../domain/strategic-model.md) and [`../../domain/context-map.md`](../../domain/context-map.md).
- accepted Bounded Contexts: `Nutrition Targeting`, `Food Knowledge`, `Market Catalog`, `Purchase Planning`.
- accepted tactical baselines exist for all four contexts; see the corresponding files under `docs/domain/`.
- ADR-002 accepts aggregated household-target optimization for the MVP while preserving member-level targets upstream.
- no target architecture is accepted yet.

## Accepted MVP simplifications

- one 30-day calculation period for needs, basket and cost;
- one current Nutrition Profile per Household Member;
- one active Nutrition Standard Set by default;
- optimizer consumes the aggregated Household Nutrition Target;
- no proof of per-member food allocation feasibility;
- no household inventory or carry-over stock;
- no actual-consumption tracking;
- no recipes/meals, cooking/preparation, portioning or storage planning;
- no medical diets, allergies or intolerances;
- no transport/travel cost between merchants;
- Product Cards and Offers may be entered manually or imported; automatic external synchronization is not required.

## Blocking tactical unknowns

Before opening S3 Architecture, resolve or explicitly defer:
1. active nutrition-standard source/version and the concrete target-derivation formulas;
2. physical-activity and growth/development-stage vocabularies;
3. canonical nutrient/unit normalization and rounding rules;
4. initial controlled top-level Food Category set and concrete variety rules;
5. Offer validity/fulfilment semantics needed for cost calculation;
6. optimization/scoring/tie-breaking policy, including partial/infeasible-plan semantics and merchant-count preference.

## Next

Continue tactical discovery with `Nutrition Targeting`, starting from the active standards/formula decision. Do not start architecture or implementation while the blocking semantic unknowns above remain unresolved.
