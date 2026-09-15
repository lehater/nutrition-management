# First implementation slice — executable planning spine

Status: `accepted` and authorized by S4; implementation completion is gated by the evidence below.
Lifecycle layer: `S4 Implementation Readiness`.

## Purpose

Implement the smallest end-to-end path that proves the accepted domain and architecture can execute without pretending to deliver the entire MVP dataset/UI.

The slice crosses all four Bounded Contexts:

`current profiles + test standard -> household target -> canonical food/market snapshot -> policy-optimal solver result -> Purchase Plan output`.

It is an architecture/product-policy validation slice, not a production-complete nutrition database or user interface.

## Authorized product path

The slice supports one synchronous command/use case:

`GeneratePurchasePlan(household_id, derivation_date, market_as_of)`

Temporal inputs are deliberately separate per ADR-011:

- `derivation_date` is the calendar date used for chronological age, Nutrition Standard applicability and the 30-day target horizon;
- `market_as_of` is a timezone-aware instant, normalized to UTC, used for Offer/Fulfilment observation and validity semantics.

A standard-library CLI adapter invokes the same use case and emits canonical structured JSON for acceptance/debugging. The CLI is an outer adapter, not a domain/API commitment.

The use case must:

1. derive current member age from date of birth at `derivation_date`;
2. validate adult profile applicability, including current-weight observation date and PAL adjustment provenance;
3. derive adult (`>=19`) maintenance energy using the accepted DGE adult formula and resolved PAL;
4. resolve a small **test-only** versioned nutrition-reference fixture through generic Nutrition Standard Set abstractions;
5. aggregate two adult member targets into one Household Nutrition Target;
6. capture one coherent executable Food Knowledge + Market Catalog snapshot using `market_as_of`;
7. run the accepted Purchase Planning policy through PySCIPOpt;
8. recalculate/report plan facts outside solver-owned reporting;
9. emit aggregate Safety Limit diagnostics without claiming member allocation safety;
10. optionally enrich positive mapped gaps with theoretical Food Knowledge suggestions;
11. emit one `mapped_complete`, `partial`, or `no_executable_plan` result with provenance, while technical failures remain separate.

## Deliberate slice boundaries

The first slice does **not** claim the full product is implemented.

Not authorized in this slice:

- full DGE/ÖGE `mvp-v1` reference-data population/import;
- full BLS 4.0 food-data import;
- NIDDK/Hall active weight-change path;
- pediatric/infant energy paths;
- pregnancy/lactation behavior;
- HTTP API or browser/mobile UI;
- authentication/authorization;
- saved Purchase Plan history;
- background/asynchronous optimization;
- external price/nutrition synchronization;
- production deployment infrastructure beyond a local single-process executable/test environment.

These accepted semantics are not deleted or replaced; they remain later implementation slices.

If the CLI receives a profile/use case outside the implemented slice capability, it must fail explicitly as implementation-not-yet-supported. It must not silently apply a fallback rule that contradicts accepted domain policy.

## Test standard fixture

End-to-end tests use an explicitly test-only Nutrition Standard Set `test-slice-v1`.

It exists only in acceptance/test data and must never be configured as the product default. Production `mvp-v1` remains the accepted product standard set; loading its complete sourced reference data is a later slice.

The fixture exercises:

- final energy target;
- a body-weight-relative adequacy reference;
- an absolute daily adequacy reference;
- an energy-relative interval/guideline;
- an upper-bound dimension;
- a separately represented Safety Limit diagnostic.

Fixture values are test evidence, not new nutrition standards.

## Acceptance catalog fixture

Use deterministic test data small enough to inspect manually but rich enough to exercise global basket planning:

- one household with two adult members and no active future weight-change goal;
- at least `8` Base Foods across at least `4` core Food Categories;
- enough canonical nutrient facts to cover the test target measures;
- focused trace/missing evidence fixtures;
- Product Cards with edible package quantities that create non-zero package surplus;
- at least `2` Merchants;
- pickup and delivery Fulfilment Channels;
- competing Offers for at least one SKU;
- a minimum-order condition;
- a delivery fee/free-delivery-threshold condition;
- unavailable, expired and future-observed Offers that must not enter the executable snapshot.

Keep the primary acceptance fixture roughly `<= 20` executable Offers. Larger synthetic data belongs to performance characterization, not correctness proof.

## Package/module layout

Use one package:

```text
src/nutrition_management/
  composition/
  adapters/
    cli/
  nutrition_targeting/
    domain/
    application/
    infrastructure/
  food_knowledge/
    domain/
    application/
    infrastructure/
  market_catalog/
    domain/
    application/
    infrastructure/
  purchase_planning/
    domain/
    application/
    infrastructure/
```

Rules:

- no project-wide shared business-domain package;
- a domain package imports neither infrastructure nor another Bounded Context;
- application code may depend on its own domain and declared ports/contracts only;
- cross-context provider contracts are exposed from provider application boundaries;
- the `composition` layer may wire all modules and technical adapters;
- SQLAlchemy/PySCIPOpt/CLI imports remain in outer layers.

## Persistence realization

Use one file-backed SQLite database and one Alembic migration stream.

Initial durable state is limited to provider-owned facts needed by the slice:

- `nt_...` household/member/profile and test standard-set/reference facts;
- `fk_...` Base Food, canonical nutrient/component/value provenance and category facts;
- `mc_...` Product Card/package, Merchant/Fulfilment Channel and Offer observations.

Purchase Planning has no durable plan/snapshot tables in this slice.

Cross-context IDs are scalar values. No cross-context SQL foreign keys or SQLAlchemy relationships.

Authoritative decimal values are persisted losslessly as canonical decimal text and converted to floating point only at the solver boundary.

## Coherent planning read

The composition/infrastructure `PlanningSnapshotSource` realizes the Purchase Planning input port.

It:

1. opens one SQLAlchemy Connection and explicit SQLite read transaction using non-legacy Python sqlite transaction control;
2. establishes one WAL read snapshot;
3. invokes provider application/read contracts backed by adapters bound to that connection;
4. derives the household nutrition target with member derivation provenance;
5. resolves executable market facts at `market_as_of`, excluding future-observed or invalid data;
6. assembles immutable input DTO/value objects;
7. closes the read transaction before optimization;
8. returns the ephemeral Planning Input Snapshot to Purchase Planning.

Database Connection/Transaction objects do not appear in domain or cross-context public contracts.

## Solver implementation shape

The solver adapter models:

- integer package counts;
- continuous planned-utilized edible quantities;
- package surplus relation;
- Offer/Fulfilment executability;
- Purchase Group minimum/order-fee/free-delivery logic;
- typed target violation/penalty facts;
- determinate versus indeterminate mapped target assessments;
- bounded variety policy;
- cost-close procurement simplification;
- final stable technical tie resolution.

Use SCIP native indicator/logical constraints for conditional decisions rather than arbitrary business big-M constants where practical.

### Sequential optimization

Implement ADR-007 as explicit sequential optimization stages. Each stage must reach solver `optimal` before its optimum is fixed for the next stage.

The accepted business stages are followed by technical tie resolution only after all business values are fixed.

For this first small slice, correctness is preferred over clever tie-breaking performance: resolve the final technical order by sequentially minimizing/fixing decision variables in canonical immutable-ID order. Do not replace it with hash weights or approximate scalarization.

Solver numeric tolerances are mechanical only. Revalidation may normalize floating-point deviations many orders of magnitude smaller than the accepted `5%`, `1%` and `25%` business thresholds, but may not redefine those thresholds.

A timeout, unknown status or merely feasible incumbent is a technical failure, not `partial`.

## Safety diagnostic boundary

Member Safety Limits remain daily member-level semantics. Because ADR-002 does not allocate household food consumption to members, the first slice may only expose an aggregate comparison diagnostic:

- compare planned utilized 30-day amount against the sum of compatible member daily upper values multiplied by 30;
- preserve unknown/indeterminate food-side evidence;
- explicitly report that there is no member-allocation guarantee;
- do not use this diagnostic to claim the plan is safe/unsafe or to alter the optimizer outcome.

## Test/evidence plan

### Unit/domain tests

Cover at least:

- exact age derivation at birthday boundary;
- male/female adult maintenance-energy formulas;
- PAL range and `+0.3` adjustment provenance rules;
- current-weight-date and body-measurement applicability;
- explicit unsupported active future weight-goal path;
- source-native reference derivation and versioned Standard Set invariants;
- 30-day scaling preserving target kind;
- nutrient missing/trace/zero distinction and canonical food/category invariants;
- effective SKU override precedence;
- Offer/Fulfilment validity, observation-time and commercial invariants;
- package purchased/planned/surplus invariants;
- typed ADR-007 target penalty functions;
- lower-bound known-proof behavior with separate unknown-evidence diagnostics;
- variety material-representation calculations;
- `mapped_complete`, `partial`, `no_executable_plan` and technical-failure semantics;
- aggregate-only safety diagnostic semantics.

### Architecture-boundary tests

Use repository-owned import/source checks. Fail the suite if:

- any `*/domain/` imports SQLAlchemy, PySCIPOpt, CLI/framework code or another context;
- a context infrastructure module imports another context's infrastructure/persistence objects;
- cross-context code bypasses published provider application contracts;
- SQL table definitions create cross-context foreign keys.

### Persistence integration tests

Use a temporary file-backed SQLite/WAL database.

Verify:

- migrations from an empty DB succeed;
- required WAL/FULL/foreign-key/read-uncommitted settings are active;
- authoritative Decimal/date/provenance facts round-trip without binary-float mutation;
- Standard Set versions can reuse stable reference IDs while exactly one set is active;
- PAL adjustment provenance round-trips;
- one planning read remains coherent when another connection commits after the first read;
- a fresh read after the transaction closes sees the committed update.

### Solver policy tests

Use tiny hand-auditable fixtures for:

- package integer rounding + continuous planned quantity;
- minimum order and one-per-Purchase-Group delivery charge;
- free-delivery threshold;
- unavailable/expired/future-observed Offer exclusion before solving;
- `mapped_complete`;
- best `partial` when nutritional/variety completion is impossible;
- `no_executable_plan` from proven hard infeasibility;
- unknown nutrient contribution/indeterminate semantics;
- 5% cost-close selection preferring fewer Purchase Groups;
- repeated identical snapshot producing the same primary plan;
- business-equivalent baskets resolved by technical tie order;
- simulated timeout/unknown never being returned as `partial`.

### End-to-end and CLI acceptance

From an empty migrated file database:

1. load test standards, household/member, food and market fixtures through provider application/import helpers;
2. invoke `GeneratePurchasePlan` with explicit `derivation_date` and timezone-aware `market_as_of`;
3. assert expected result kind, selected lines, package counts, planned quantities, Purchase Groups, total cost, mapped diagnostics, target-member provenance and market provenance;
4. invoke the identical request again and assert byte-stable canonical JSON;
5. invoke the standard-library CLI over the same database and assert it drives the same application use case and emits stable canonical JSON.

## Performance characterization

Performance is evidence, not a product SLA.

The slice contains a repeatable synthetic benchmark that records:

- number of Base Foods/SKUs/Offers;
- number of mapped target dimensions;
- number of sequential solver stages;
- maximum solver variables/constraints observed per stage;
- runtime environment;
- wall-clock time and final solver status.

At minimum characterize an acceptance-scale case and one larger synthetic catalog. Store the successful CI evidence under `docs/baseline/`; do not add queues/workers or weaken optimization semantics to hide slow solving.

If policy-optimal synchronous solving is not practically usable on a plausible MVP catalog, stop expansion and reopen S3 with measured evidence.

## Implementation completion gate for this slice

The slice is complete only when:

- dependency lock is committed and reproducible with `uv sync --locked`;
- migrations work from an empty file DB;
- all unit/integration/architecture/solver/E2E/CLI tests pass on the target stack;
- no accepted architecture boundary is bypassed;
- no production claim is made from `test-slice-v1` fixture data;
- no solver result is accepted without proven policy optimality/hard infeasibility;
- performance characterization is recorded from a successful target-stack CI run;
- unresolved failures are classified at their owning layer instead of patched with semantic fallbacks.

## Follow-up slices after this one

Expected, not yet authorized here:

1. complete sourced `mvp-v1` nutrition-standard data + target mappings;
2. BLS 4.0 theoretical-food import and provenance validation;
3. broader Market Catalog/import workflows;
4. NIDDK/Hall adult weight-goal path and remaining accepted age paths;
5. user-facing application/API/UI only after the core result proves useful.
