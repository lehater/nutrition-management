# First implementation slice — executable planning spine

Status: `accepted` when S4 gate passes.
Lifecycle layer: `S4 Implementation Readiness`.

## Purpose

Implement the smallest end-to-end path that proves the accepted domain and architecture can execute without pretending to deliver the entire MVP dataset/UI.

The slice must cross all four Bounded Contexts:

`current profiles + standard fixture -> household target -> canonical food/market snapshot -> policy-optimal solver result -> Purchase Plan output`.

It is an architecture/product-policy validation slice, not a production-complete nutrition database or user interface.

## Authorized product path

The slice supports one synchronous command/use case:

`GeneratePurchasePlan(household_id, as_of_date)`

A standard-library CLI adapter invokes that use case and emits a structured JSON result for acceptance/debugging. The CLI is an outer adapter, not a domain/API commitment.

The use case must:

1. derive current member age from date of birth at `as_of_date`;
2. derive adult (`>=19`) maintenance energy using the accepted DGE adult formula and resolved PAL;
3. resolve a small **test-only** versioned nutrition-reference fixture through the generic Nutrition Standard Set abstractions;
4. aggregate two adult member targets into one Household Nutrition Target;
5. capture one coherent executable Food Knowledge + Market Catalog snapshot;
6. run the accepted Purchase Planning policy through PySCIPOpt;
7. recalculate/report plan facts outside solver-owned reporting;
8. optionally enrich positive mapped gaps with theoretical Food Knowledge suggestions;
9. emit one `mapped_complete`, `partial`, or `no_executable_plan` result with provenance, while technical failures remain separate.

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
- deployment infrastructure beyond a local single-process executable/test environment.

These accepted semantics are not deleted or replaced; they remain later implementation slices.

If the CLI receives a profile/use case outside the implemented slice capability, it must fail explicitly as implementation-not-yet-supported. It must not silently apply a fallback rule that contradicts accepted domain policy.

## Test standard fixture

End-to-end tests use an explicitly test-only Nutrition Standard Set such as `test-slice-v1`.

It exists only in acceptance/test data and must never be configured as the product default. Production `mvp-v1` remains the accepted product standard set; loading its complete sourced reference data is a later slice.

The test fixture should be intentionally small but exercise different target bases/semantics, for example:

- final energy target;
- one body-weight-relative adequacy reference;
- one absolute daily adequacy reference;
- one energy-relative guideline/interval;
- one upper-bound or point-guideline dimension;
- one separately represented safety diagnostic.

Exact fixture values are test evidence, not new nutrition standards.

## Acceptance catalog fixture

Use deterministic test data small enough to inspect manually but rich enough to exercise global basket planning:

- one household with **two adult members**, no active weight-change goal;
- at least `8` Base Foods across at least `4` core Food Categories;
- enough canonical nutrient facts to cover the test target measures;
- at least one unknown/trace nutrient value in a focused policy fixture;
- Product Cards with edible package quantities that create non-zero package surplus;
- at least `2` Merchants;
- pickup and delivery Fulfilment Channels;
- competing Offers for at least one SKU;
- one minimum-order condition;
- one delivery fee/free-delivery-threshold condition;
- one unavailable or expired Offer that must not enter the executable snapshot.

Keep the primary acceptance fixture to roughly `<= 20` executable Offers. Larger synthetic data belongs to performance characterization, not correctness proof.

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

Initial durable state is limited to accepted provider-owned facts needed by the slice:

- `nt_...` current household/member/profile and test standard-set/reference facts;
- `fk_...` Base Food, nutrient/component/value provenance and category facts;
- `mc_...` Product Card/package, Merchant, Fulfilment Channel and Offer observations.

Purchase Planning needs no durable tables in this slice unless a concrete implementation need emerges that is consistent with S3; plan/snapshot persistence must not be introduced by convenience.

Cross-context IDs are scalar values. No cross-context SQL foreign keys and no cross-context SQLAlchemy table relationships.

## Coherent planning read

Implement a composition/infrastructure `PlanningSnapshotSource` (name may vary) that realizes the Purchase Planning input port.

It:

1. opens one SQLAlchemy Connection and explicit SQLite read transaction;
2. establishes the read snapshot;
3. invokes provider application/read contracts backed by adapters bound to that connection;
4. assembles immutable input DTO/value objects;
5. closes the read transaction;
6. returns the ephemeral Planning Input Snapshot to Purchase Planning.

Database Connection/Transaction objects must not appear in domain or cross-context public contract signatures.

## Solver implementation shape

The solver adapter models:

- integer package counts;
- continuous planned-utilized edible quantities;
- package surplus relation;
- Offer/Fulfilment executability;
- Purchase Group minimum/order-fee logic;
- typed target violation/penalty facts;
- indeterminate mapped target count when selected planned quantities use unknown composition;
- bounded variety policy;
- cost-close procurement simplification;
- final stable technical tie resolution.

Prefer SCIP native indicator/logical constraints for conditional decisions rather than arbitrary big-M constants.

### Sequential optimization

Implement ADR-007 as explicit sequential optimization stages. Each stage must reach solver `optimal` before its optimum is fixed for the next stage.

The accepted business stages are followed by technical tie resolution only after all business values are fixed.

For this first small slice, correctness is preferred over clever tie-breaking performance: resolve the final technical order by sequentially minimizing/fixing decision variables in canonical immutable-ID order as needed. Do not replace it with hash weights or approximate scalarization.

If this becomes a runtime bottleneck on larger data, record evidence and improve the implementation without weakening the order; reopen S3 if a semantic change is proposed.

## Test/evidence plan

### Unit tests

Cover at least:

- exact age derivation at birthday boundary;
- male/female adult maintenance-energy formulas;
- source-native reference derivation for fixture bases;
- 30-day scaling preserving target kind;
- nutrient missing/trace/zero distinction;
- effective SKU override precedence;
- Offer/Fulfilment validity and order-cost calculations;
- package purchased/planned/surplus invariants;
- typed ADR-007 target penalty functions;
- variety material-representation calculations;
- plan outcome classification.

### Architecture-boundary tests

Use a simple repository-owned import graph/source check rather than adding an architecture framework.

Fail the test suite if, for example:

- any `*/domain/` imports SQLAlchemy, PySCIPOpt, CLI/framework code or another context;
- a context infrastructure module imports another context's infrastructure/persistence objects;
- cross-context code imports anything except explicitly published provider application contracts;
- SQL table definitions create cross-context foreign keys.

### Persistence integration tests

Use a temporary file-backed SQLite/WAL database.

Verify:

- migrations from empty DB succeed;
- foreign-key pragma and WAL configuration are active;
- context repositories round-trip authoritative decimal/date/provenance facts without unintended binary-float mutation;
- a planning read snapshot remains coherent when another connection commits an Offer change after the first read in the planning transaction;
- after the read transaction closes, a new read sees the committed update.

### Solver policy tests

Use tiny, hand-auditable fixtures with expected outcomes for:

- package integer rounding + continuous planned quantity;
- minimum order and one-per-Purchase-Group delivery charge;
- free-delivery threshold;
- unavailable/expired Offer exclusion;
- `mapped_complete`;
- best `partial` when nutritional/variety completion is impossible;
- `no_executable_plan` from proven hard infeasibility;
- unknown nutrient contribution causing indeterminate assessment;
- 5% cost-close selection preferring fewer Purchase Groups;
- same snapshot repeated multiple times producing the same primary plan;
- two business-equivalent baskets resolved by the technical tie order;
- simulated solver timeout/unknown never being returned as `partial`.

### End-to-end acceptance test

From an empty migrated test database:

1. load the test standard, household/member, food and market fixtures through application/import test helpers (not direct table inserts except migration-owned seed mechanics if explicitly justified);
2. call the same Generate Purchase Plan use case used by the CLI;
3. assert expected result kind, selected lines, package counts, planned quantities, Purchase Groups, total cost, mapped diagnostics and provenance;
4. invoke the identical request again and assert a byte-stable canonical JSON result, excluding no volatile fields because the acceptance request supplies its explicit `as_of_date`.

## Performance characterization

Performance is evidence, not a new product SLA.

During the slice, add a repeatable synthetic benchmark that records:

- number of Base Foods/SKUs/Offers;
- number of mapped target dimensions;
- number of solver variables/constraints/stages;
- hardware/runtime environment;
- wall-clock time and final solver status for every sequential stage.

At minimum characterize the acceptance-scale fixture and one larger synthetic catalog. Do not add queues/workers/timeouts-as-domain-results to hide slow solving.

If policy-optimal synchronous solving is not practically usable on a plausible MVP catalog, stop expansion and reopen S3 with measured evidence before introducing asynchronous execution or weakening optimization semantics.

## Implementation completion gate for this slice

The slice is complete only when:

- dependency lock is committed and reproducible with `uv sync --locked`/equivalent frozen mode;
- migrations work from an empty file DB;
- all unit/integration/architecture/solver/acceptance tests pass;
- no accepted architecture boundary is bypassed;
- no production claim is made from `test-slice-v1` fixture data;
- no solver result is accepted without proven policy optimality/hard infeasibility;
- performance characterization is recorded;
- unresolved failures are classified at their owning layer instead of patched with semantic fallbacks.

## Follow-up slices after this one

Expected, not yet authorized here:

1. complete sourced `mvp-v1` nutrition-standard data + target mappings;
2. BLS 4.0 theoretical-food import and provenance validation;
3. broader Market Catalog/import workflows;
4. NIDDK/Hall adult weight-goal path and remaining accepted age paths;
5. user-facing application/API/UI only after the core result proves useful.
