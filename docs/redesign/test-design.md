# Test Design — Redesign Baseline

Status: accepted canonical pre-code test design.

Owner: TEST-DESIGN.

## Boundary

Verification Design owns what evidence classes are required to accept the system.

Test Design owns executable behavioral contracts and scenario catalogues that produce that evidence.

Implementation Design owns how the product is realized.

Test implementation owns concrete test code, framework mechanics, fixtures/builders and local assertion syntax.

Existing implementation and existing tests are not design authority for this artifact.

## Traceability rule

Every test contract traces to accepted requirements/domain/component/verification knowledge.

A test contract specifies observable inputs/preconditions, operation, expected outcome/invariants and evidence class. It does not prescribe production implementation internals.

## Test contract catalogue

### TD-NT-01 — target derivation is explicit and reproducible

Given an accepted household/member profile set, explicit derivation date and applicable Nutrition Standard Set version, deriving targets twice from identical canonical facts yields semantically identical target values and provenance.

Reference/desired values remain distinct from safety limits.

### TD-NT-02 — unsupported applicability remains unsupported

Given a profile for which the active standard has no supported applicability/mapping, target derivation produces the accepted unsupported/indeterminate outcome rather than silently choosing a nearby profile, zero or default.

### TD-FK-01 — nutrient evidence states are not collapsed

For every accepted nutrient evidence state, canonicalization and retrieval preserve its semantic kind.

Only states explicitly defined as quantitative participate as exact numeric amounts.

### TD-FK-02 — provenance survives normalization

Given external nutrient evidence with accepted source identity, basis/unit/component and provenance, normalization may change representation but cannot lose required provenance.

### TD-MC-01 — executable offer is time-explicit

Given Offers differing in availability/validity/observation time, the executable market projection for explicit `as_of` contains only Offers permitted by accepted Market Catalog semantics.

No current-clock value may alter the result.

### TD-MC-02 — package semantics are preserved

Given Product/Offer facts, executable market contracts preserve edible package quantity, price, currency and accepted order-group conditions without conflating purchased package quantity with utilized edible quantity.

### TD-PP-01 — planning input capture is immutable and coherent

Given explicit household, derivation date and market-as-of, one capture produces an immutable Planning Input whose provider facts are mutually coherent according to the accepted read boundary.

After capture, optimization cannot observe later provider changes.

### TD-PP-02 — optimization cannot query providers

During optimization, all required product/domain facts are supplied by Planning Input.

A test substitute that fails on any provider access after capture must not be invoked.

### TD-PP-03 — hard infeasibility differs from technical failure

Hard-model infeasibility produces the accepted no-plan/hard-infeasible domain result.

Timeout/unknown/numeric/adapter failure without required optimality proof is technical failure and must not promote an incumbent to the primary plan.

### TD-PP-04 — authoritative reporting is solver-independent

Given accepted Planning Input and solver-independent decision, coverage, cost, variety, package surplus and result classification are recalculated by Plan Evaluation/Reporting.

Inconsistent solver-native report values cannot become authoritative output.

### TD-PP-05 — lexicographic policy cannot be traded across stages

Where improving a later objective would worsen an earlier objective, the selected result preserves the proven optimum of every earlier business stage before considering the later stage.

### TD-PP-06 — purchased and utilized quantities remain distinct

For a package whose purchased edible quantity exceeds utilized quantity, cost/procurement use purchased package quantity while nutrient contribution uses accepted utilized quantity semantics.

### TD-PP-07 — theoretical suggestions are post-plan advisory

For an accepted result with eligible mapped positive gaps, theoretical suggestions occur after executable planning.

Changing/removing suggestions cannot change basket selection or primary outcome classification.

### TD-ARCH-01 — dependency ownership

Structural verification rejects:
- domain/application policy depending on persistence, solver or presentation frameworks;
- consumer context depending on provider persistence representation;
- optimization depending on providers during solve;
- external adapters bypassing application contracts to datastore/domain policy.

### TD-CONTRACT-01 — provider contract substitutability

Every provider application contract consumed by Planning Input Capture can be replaced by a conforming test substitute without requiring provider persistence/framework objects.

### TD-PERSIST-01 — semantic round-trip

For every authoritative persisted value class — Decimal, date/time, currency, evidence state/provenance and identifiers — persistence round-trip preserves the accepted semantic value exactly.

### TD-CLI-01 — canonical deterministic external result

Given identical explicit CLI inputs and identical canonical provider state, repeated successful invocations produce semantically identical canonical JSON.

### TD-CLI-02 — semantic time inputs are mandatory

Omitting required derivation date or market-as-of is an interface usage error.

The application must not substitute current date/time.

### TD-CLI-03 — technical failure cannot masquerade as domain outcome

Injected optimization/persistence technical failure remains distinguishable from accepted full/partial/no-plan domain results.

## Property-oriented contracts

Use generated/property-style coverage where useful for:
- nutrient evidence-state preservation;
- Decimal round-trip;
- deterministic canonical serialization;
- non-negative/integer package constraints;
- monotonic preservation of earlier lexicographic optima;
- stable identity/provenance mapping.

No specific property-testing library is mandated.

## Contract versus implementation test split

### Required before production behavior for a TDD slice

Materialize applicable public behavioral/contract scenarios first and establish RED for the intended missing behavior.

### Implementation-local freedom

Private-helper tests, fixture builders, parametrization layout, mocking library, test-file organization and non-semantic implementation-mechanic tests remain coding freedoms.

### Not product truth

Do not treat the following as product contracts unless another accepted artifact explicitly requires them:
- private method names;
- exact class counts;
- SQL statement shape;
- SCIP internal variable names;
- ORM mapping internals beyond semantic persistence/ownership obligations;
- incidental call counts/order.

## TDD execution protocol

For each Implementation Design slice:

1. select applicable Test Design contracts;
2. materialize the smallest executable tests;
3. establish RED for the intended missing behavior;
4. implement the minimum production behavior satisfying accepted design;
5. establish GREEN;
6. refactor without changing accepted behavior/contracts;
7. run applicable architecture/integration/property evidence;
8. if satisfying the test requires a new semantic decision, stop and open an upstream Question.

RED/GREEN history is implementation-process evidence, not semantic project truth unless explicitly required.

## Acceptance conclusion

Verification Design and Test Design are independent knowledge:

- Verification Design defines required evidence categories.
- Test Design defines executable observable contracts/scenarios/properties.
- Test code remains downstream and framework-local.

This Test Design is required by terminal backend/CLI Implementation Design.
