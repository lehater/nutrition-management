# ADR-007 — MVP Purchase Planning uses a lexicographic nutrition-first optimization policy

Status: `accepted`.

Date: 2026-09-15.

## Context

Purchase Planning must choose concrete packages and commercial Offers while balancing nutritional coverage, energy fit, dietary variety, total acquisition cost and procurement simplicity.

These dimensions have different units and semantics. A single weighted sum would require arbitrary exchange rates such as how many euros equal one percentage point of nutrient deficit or one additional food category. Such weights would be difficult to explain and would let small changes in one dimension silently compensate for materially different failures in another.

Nutrition Targeting also publishes typed references rather than homogeneous `[min,max]` ranges, and ADR-002 prevents aggregate household optimization from claiming member-level food allocation or safety.

## Decision

### One primary recommendation

The MVP produces one primary recommended Purchase Plan for a calculation run. It may expose diagnostics and gap-closing Base Food suggestions, but a Pareto-style shortlist is deferred until there is demonstrated product value.

### Executability constraints

A candidate basket is executable only when:

- package counts are non-negative integers;
- every selected Product Card has an executable edible-quantity conversion;
- every selected Offer is `available` and satisfies explicit Offer validity bounds;
- every selected Fulfilment Channel satisfies explicit channel validity bounds;
- selected Offers/order charges use one compatible currency;
- each used Purchase Group satisfies its channel minimum-order condition;
- channel-level fulfilment/delivery fees are applied exactly once per Purchase Group.

These are market/purchase feasibility constraints, not nutrition-scoring dimensions.

### Deterministic nutrient evidence

Coverage arithmetic uses accepted target-to-food Nutrient Measure mappings only.

Known numeric values and known zero values provide deterministic evidence. Trace/unknown composition is never silently treated as zero.

For a lower-bound target, the sum of known contributions can prove a minimum amount; unknown contributions remain flagged uncertainty and do not contribute to the proven amount.

For an upper-bound, interval or point-guideline assessment, unknown selected-food contribution makes that measure `indeterminate` because compliance cannot be proven.

Plans with fewer indeterminate mapped target assessments are preferred before cost optimization.

Unmapped Nutrition References remain visible as unsupported coverage dimensions and cannot be reported as satisfied.

### Typed target evaluation

For a derived household amount `x`:

#### Recommended intake / estimated-value point

Treat the reference `L` as an adequacy floor for planning:

`violation = max(0, (L - x) / L)`.

Amounts above `L` do not create an ordinary excess penalty. Applicable upper guidance or safety information is handled separately.

#### Lower-bound guideline

For lower bound `L`:

`violation = max(0, (L - x) / L)`.

#### Upper-bound guideline

For upper bound `U`:

`violation = max(0, (x - U) / U)`.

#### Interval guideline

For `[L, U]`:

- `0` when `L <= x <= U`;
- `(L - x) / L` when `x < L`;
- `(x - U) / U` when `x > U`.

#### Point guideline

A source point guideline `T` remains a point upstream. Purchase Planning defines an MVP optimization tolerance of `±5%` around it.

- penalty is `0` for `0.95T <= x <= 1.05T`;
- outside that band, penalty is relative distance from the nearest band edge.

This tolerance is optimizer policy, not a rewritten Nutrition Reference.

#### Energy target

The final household energy target is evaluated as a point-guideline dimension with the same `±5%` zero-penalty band. Outside the band, relative deviation from the nearest edge is penalized.

### Safety-limit treatment

Member-level Safety Limits are not hard constraints and do not contribute to a claim of plan safety in the MVP because the system does not model per-member allocation or actual consumption.

Where a compatible aggregate comparison signal can be derived, it is reported as a warning/diagnostic only. It does not convert an EFSA UL into a household preferred maximum and does not make the plan `safe` or `unsafe` by itself.

### Nutritional ranking

For each executable candidate, Purchase Planning forms these ordered quality facts:

1. number of indeterminate mapped target assessments — lower is better;
2. maximum normalized directed-target violation — lower is better;
3. mean normalized directed-target violation — lower is better;
4. maximum point-guideline/energy penalty — lower is better;
5. mean point-guideline/energy penalty — lower is better.

Candidates are compared lexicographically in this order. Once a dimension reaches zero, no additional benefit is created by oversupplying that condition.

This makes adequacy failures dominate cost without inventing cross-unit nutritional weights, while still distinguishing partial plans when full coverage is impossible.

### Variety target

Variety uses the Food Knowledge material-representation semantics from ADR-005.

The MVP variety target is satisfied when all three conditions hold:

- at least `4` of the `6` core top-level Food Categories are materially represented;
- at least `8` distinct Base Foods are materially represented;
- no single Base Food contributes more than `25%` of total plan food energy.

These thresholds are explicit MVP planning heuristics, not DGE population recommendations or medical claims.

Variety penalty is evaluated only until these targets are met; adding more categories/foods or reducing concentration further does not outrank cost once the variety target is satisfied.

When no candidate can satisfy all three, prefer in order:

1. greater number of materially represented core categories, capped at `4`;
2. greater number of materially represented Base Foods, capped at `8`;
3. lower maximum single-Base-Food energy share until `25%` is reached.

### Cost and procurement simplicity

After nutritional quality and variety are optimized, Purchase Planning minimizes total acquisition cost:

`total cost = line package costs + applicable Purchase Group fulfilment/delivery fees`.

Unavoidable package surplus affects purchased quantity/cost and nutrient totals because the basket consists of whole packages, but it does not create inventory state.

Let `Cmin` be the minimum total cost among candidates tied on the preceding nutrition/variety policy. A candidate is `cost-close` when:

`candidate_cost <= 1.05 × Cmin`.

Among cost-close candidates, prefer lexicographically:

1. fewer Purchase Groups;
2. fewer distinct Merchants;
3. lower total acquisition cost;
4. lower total edible package surplus mass as the final deterministic business tie-breaker.

Thus the MVP may pay up to 5% above the absolute cheapest nutrition/variety-equivalent basket to materially simplify procurement.

### Plan outcome semantics

An executable result is classified as:

- `complete` — all supported mapped target assessments are determinate and have zero nutrition/energy penalty under the policy, and the variety target is satisfied;
- `partial` — an executable basket exists but at least one supported target is violated/indeterminate or the variety target cannot be met;
- `no_executable_plan` — no non-empty basket can be constructed from executable Offers under current market constraints.

A `partial` plan is still returned when it is the best available result. It must report every material violation/indeterminate dimension and must not be described as fully nutritionally adequate.

Unmapped source references are reported separately as `unsupported coverage`; they do not become false zero gaps and do not prevent the mapped portion of a plan from being optimized.

### Gap-closing theoretical suggestions

For each positive lower-bound/adequacy gap with an accepted Nutrient Measure mapping, Food Knowledge theoretical Base Foods with a known positive amount of the missing measure are eligible suggestions.

MVP ranking:

1. higher amount of the missing Nutrient Measure per `100 kcal` of food, when food energy is positive and known;
2. then higher amount per `100 g edible portion`;
3. then prefer a Base Food from a core variety category not yet materially represented in the current plan;
4. deterministic Base Food identity as final stable tie-breaker.

For an energy gap itself, rank by `ENERCC` per `100 g edible portion` rather than the trivial per-100-kcal measure.

Suggestions are theoretical Food Knowledge output. Without an executable Product Card/Offer they cannot be inserted as Purchase Plan lines.

## Consequences

- optimizer priorities are explainable without a single arbitrary cross-unit weighted score;
- adequately covered nutrients are not rewarded for unlimited oversupply;
- recommended/estimated intake points behave as adequacy floors rather than hard equalities;
- point-guideline tolerance is explicitly downstream Purchase Planning policy;
- unknown composition produces indeterminate evidence instead of false precision;
- safety-limit diagnostics remain honest about the absence of member allocation/consumption semantics;
- variety has a finite target, so tiny improvements in variety cannot justify unlimited extra cost;
- `5%` gives concrete meaning to “close in value” for procurement simplification;
- a single primary plan keeps the MVP output simple while retaining enough diagnostics to explain partial results.

## Alternatives considered

### One weighted objective over nutrition, variety, euros and merchant count

Rejected because weights would embed opaque exchange rates between semantically different concerns and would be hard to validate before real usage data exists.

### Make every nutrition reference a hard constraint

Rejected because S1 explicitly treats optimization dimensions as advisory trade-offs and the purchasable catalog may not permit complete coverage. The system must return and explain the best partial plan instead of simply failing.

### Treat safety limits as aggregate household hard maxima

Rejected because ADR-002 does not prove member allocation and the product does not model actual consumption; such a constraint would imply a safety guarantee the model cannot support.

### Always choose the absolute cheapest plan after nutrition

Rejected because S1 explicitly prefers simpler procurement when alternatives are close. The 5% cost-close band makes that preference concrete and bounded.

### Emit a Pareto frontier in MVP

Rejected for KISS. One recommendation plus transparent diagnostics is sufficient to validate the end-to-end product value first.

## Supersession

Supersedes: none.
Superseded by: none.
