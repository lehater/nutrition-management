# Test Design — Nutrition Management

Status: accepted canonical pre-code test design.
Constraint: derived only from accepted design knowledge. Existing implementation and existing tests are not evidence and are not inputs.

## Authority boundary

Verification Design owns **what evidence classes are required to accept the system**.

Test Design owns **the executable behavioral contracts and scenario catalogue that will produce that evidence**.

Implementation Design owns **how the product is realized**.

Test implementation owns **the concrete test code, framework mechanics, fixtures/builders and local assertion syntax**.

## Traceability rule

Every test contract below traces to accepted requirements/domain/component/verification knowledge. A test contract specifies observable inputs/preconditions, operation, expected outcome/invariants and evidence class. It does not prescribe production implementation internals.

## Test contract catalogue

### TD-NT-01 — target derivation is explicit and reproducible

Given an accepted household/member profile set, an explicit derivation date and an explicit applicable nutrition-standard version, deriving targets twice from identical canonical facts yields semantically identical target values and provenance.

Must distinguish reference/desired values from safety limits.

Evidence: Nutrition Targeting behavior.

### TD-NT-02 — unsupported applicability remains unsupported

Given a profile for which an accepted standard has no supported applicability/mapping, target derivation produces the accepted unsupported/indeterminate domain outcome rather than silently choosing a nearby profile, zero or default.

Evidence: Nutrition Targeting behavior and fail-safe semantics.

### TD-FK-01 — nutrient evidence states are not collapsed

For each accepted evidence state (quantitative known value, known zero, trace, unknown/missing, limit-qualified state as defined upstream), canonicalization and retrieval preserve its semantic kind.

Only states explicitly defined as quantitative participate as exact numeric amounts.

Evidence: Food Knowledge semantics/persistence.

### TD-FK-02 — provenance survives normalization

Given external nutrient evidence with accepted source identity, basis/unit/component and provenance, normalization may change representation but cannot lose the source/provenance required by the canonical contract.

Evidence: Food Knowledge provenance.

### TD-MC-01 — executable offer is time-explicit

Given offers differing in availability/validity/observation time, the executable market projection for explicit `as_of` contains only offers permitted by accepted Market Catalog semantics.

No current-clock value may alter the result.

Evidence: Market Catalog behavior.

### TD-MC-02 — package semantics are preserved

Given product/package facts, executable offers preserve edible package quantity, price, currency and accepted order-group conditions without conflating purchased package quantity with utilized edible quantity.

Evidence: Market Catalog behavior/persistence.

### TD-PP-01 — planning input capture is immutable and coherent

Given explicit household, derivation date and market-as-of, one capture produces an immutable Planning Input whose provider facts are mutually coherent according to the accepted read boundary.

After capture, optimization cannot observe later provider changes.

Evidence: coherent-capture integration.

### TD-PP-02 — optimization cannot query providers

During optimization, all required product/domain facts are supplied by Planning Input. A test substitute that fails on any provider access after capture must not be invoked.

Evidence: component/architecture boundary.

### TD-PP-03 — hard infeasibility differs from technical failure

For an input whose hard model constraints have no feasible solution, the application reports the accepted no-plan/hard-infeasible domain result.

For timeout/unknown/numeric/adapter failure without the required optimality proof, it reports technical failure and must not promote an incumbent to the primary plan.

Evidence: optimization adapter and outcome semantics.

### TD-PP-04 — authoritative reporting is solver-independent

Given an accepted Planning Input and solver-independent decision, coverage, cost, variety, package surplus and result classification are recalculated by Plan Evaluation/Reporting. Deliberately inconsistent solver-native report values cannot become authoritative output.

Evidence: Purchase Planning/reporting.

### TD-PP-05 — lexicographic policy cannot be traded across stages

Construct accepted planning scenarios where improving a later objective would worsen an earlier objective. The selected result must preserve the proven optimum of every earlier business stage before considering the later stage.

Evidence: deterministic planning policy.

### TD-PP-06 — purchased and utilized quantities remain distinct

For a package whose purchased edible quantity exceeds the amount utilized by the plan, cost/procurement use purchased package quantity while nutrient contribution uses the accepted utilized quantity semantics.

Evidence: Purchase Planning invariants.

### TD-PP-07 — theoretical suggestions are post-plan advisory

For a partial/no-executable result with eligible mapped positive gaps, suggestions may be requested after executable planning. Changing/removing suggestions cannot change basket selection or primary outcome classification.

Evidence: cross-context application behavior.

### TD-ARCH-01 — dependency ownership

Structural verification must reject:
- domain/application policy depending on persistence, solver or presentation frameworks;
- a consumer context depending on provider persistence representation;
- optimization depending on providers during solve;
- external adapters bypassing application contracts to datastore/domain policy.

Evidence: architecture/component boundaries.

### TD-CONTRACT-01 — provider contract substitutability

Each provider application contract used by Planning Input Capture can be replaced by a conforming test substitute without requiring provider persistence/framework objects.

Evidence: component contracts/DIP.

### TD-PERSIST-01 — semantic round-trip

For each authoritative persisted value class (decimal amount, date/time, currency, evidence state/provenance and identifiers), persistence round-trip preserves the accepted semantic value exactly.

Evidence: persistence design.

### TD-CLI-01 — canonical deterministic external result

Given identical explicit CLI inputs and identical canonical provider state, repeated successful invocations produce semantically identical canonical JSON.

Evidence: interface contract.

### TD-CLI-02 — semantic time inputs are mandatory

Omitting required derivation date or market-as-of is an interface usage error. The application must not substitute current date/time.

Evidence: interface/ADR-009/011.

### TD-CLI-03 — technical failure cannot masquerade as domain outcome

Inject an optimization/persistence technical failure. External behavior must be distinguishable from accepted full/partial/no-plan domain results.

Evidence: external contract/failure semantics.

## Property-oriented contracts

Example-based scenarios are insufficient for several invariants. Test implementation should use generated/property-style coverage where useful for:

- nutrient evidence-state preservation;
- decimal round-trip;
- deterministic canonical serialization;
- non-negative/integer package constraints;
- monotonic preservation of earlier lexicographic optima;
- stable identity/provenance mapping.

The Test Design requires these properties but does not mandate a property-testing library.

## Contract versus implementation test split

### Must exist before production behavior is written

For a TDD slice, materialize the applicable public behavioral/contract scenarios first and observe them fail for the intended missing behavior.

### May be designed locally during implementation

Private-helper tests, fixture builders, parametrization layout, mocking library choice, test file organization and tests of non-semantic implementation mechanics remain coding freedoms.

### Must not be tested as product truth

- private method names;
- exact class counts;
- SQL statement shape unless required by an accepted quality/transaction contract;
- SCIP internal variable names;
- ORM mapping internals beyond semantic persistence/ownership obligations;
- incidental call counts/order unless the design contract makes them observable.

## TDD execution protocol

For each Implementation Design slice:

1. select applicable Test Design contracts;
2. materialize the smallest executable test(s) expressing those contracts;
3. establish RED for the intended missing behavior, not for broken test setup;
4. implement the minimum production behavior that satisfies accepted design;
5. establish GREEN;
6. refactor without changing accepted behavior/contracts;
7. run applicable architecture/integration/property evidence;
8. if satisfying the test requires a new semantic decision, stop and open an upstream Question.

TDD is an implementation method here; Test Design is upstream knowledge. Harness should not require RED/GREEN history as semantic truth unless a project explicitly chooses process evidence.

## Design rationale

The catalogue adds information not contained in Verification Design alone. For example, Verification Design says to verify coherent capture and solver failure separation; Test Design fixes concrete observable distinctions such as provider mutation after capture, provider-access prohibition during solve, incumbent rejection on unfinished optimization and deliberately inconsistent solver-native reporting.

It also adds information not owned by Implementation Design: the selected SQLite/SQLAlchemy/SCIP realization does not determine these expected outcomes.

Therefore Test Design has a candidate independent responsibility boundary.

## Harness model

Authority: `TEST-DESIGN`.

Capability: `nutrition-management.test-design`.

Prerequisites:
- requirements;
- domain contracts;
- architecture;
- application design;
- data design;
- interface design;
- component design;
- verification design;
- implementation design only where technology-specific test contracts are genuinely required.

Semantic Test Design precedes terminal Implementation Design. Technology-specific test mechanics may be refined during implementation without moving semantic test truth downstream.

## Acceptance conclusion

Nutrition provides positive evidence that Verification Design and Test Design are not identical:

- Verification Design defines required evidence categories.
- Test Design defines executable observable contracts/scenarios/properties.
- test code remains downstream and framework-local.

The candidate boundary reduces coding-agent freedom over *what to test* without dictating *how test code is written*.

The Test Design is accepted as project engineering knowledge. Harness-level portability/canonicalization remains independently governed by Harness.

