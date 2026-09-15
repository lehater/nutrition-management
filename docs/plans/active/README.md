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
- ADR-003 accepts Nutrition Standard Set `mvp-v1`, sourced nutrient/safety semantics, DGE/PAL energy derivation and the adult NIDDK/Hall weight-goal policy.
- no target architecture is accepted yet.

## Accepted MVP simplifications

- one 30-day calculation period for needs, basket and cost;
- one current Nutrition Profile per Household Member;
- one active Nutrition Standard Set by default; current active set is `mvp-v1`;
- optimizer consumes the aggregated Household Nutrition Target;
- no proof of per-member food allocation feasibility or member-level safety from aggregate basket totals;
- no automatic pediatric target-weight energy adjustment;
- no household inventory or carry-over stock;
- no actual-consumption tracking;
- no recipes/meals, cooking/preparation, portioning or storage planning;
- no medical diets, allergies or intolerances;
- no transport/travel cost between merchants;
- Product Cards and Offers may be entered manually or imported; automatic external synchronization is not required.

## Recently resolved

- active nutrition-standard sources/version: resolved by [`../../domain/nutrition-standard-set-mvp-v1.md`](../../domain/nutrition-standard-set-mvp-v1.md) and [`../../decisions/ADR-003-nutrition-targeting-standards-and-derivation.md`](../../decisions/ADR-003-nutrition-targeting-standards-and-derivation.md);
- concrete energy/weight-goal/nutrient-reference derivation policy: resolved by the same artifacts;
- physical-activity vocabulary: resolved to numeric DGE PAL semantics in `mvp-v1`.

## Blocking tactical unknowns

Before opening S3 Architecture, resolve or explicitly defer:
1. development/growth/physiological-state vocabulary and applicability, including whether pregnancy/lactation belongs in the MVP profile;
2. canonical nutrient identities, unit normalization/conversions and rounding rules shared semantically between Nutrition Targeting and Food Knowledge;
3. initial controlled top-level Food Category set and concrete variety rules;
4. Offer validity/fulfilment semantics needed for cost calculation;
5. optimization/scoring/tie-breaking policy, including typed-target treatment, safety-limit handling, partial/infeasible-plan semantics and merchant-count preference.

## Next

Finish the remaining `Nutrition Targeting` blocker by resolving development/growth/physiological-state semantics. Then close canonical nutrient/unit semantics needed to connect Nutrition Targeting to Food Knowledge. Do not start architecture or implementation while the blocking semantic unknowns above remain unresolved.
