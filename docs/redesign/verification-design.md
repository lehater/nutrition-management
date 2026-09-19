# Verification Design — Redesign Baseline

Status: accepted.

Verification evidence is derived from design contracts, not from current implementation/tests.

## Required evidence classes

### Nutrition Targeting

Demonstrate deterministic derivation for explicit date/version/profile inputs; preservation of source semantic kind, unsupported applicability, mappings, provenance and separate safety limits.

### Food Knowledge

Demonstrate all accepted nutrient evidence states remain distinguishable; only quantitative states participate in exact arithmetic; normalization preserves component/unit/basis/provenance.

### Market Catalog

Demonstrate package edible quantity, availability, currency, price, observation/validity and order-group conditions determine executability at explicit as-of time.

### Purchase Planning

Demonstrate lexicographic nutrition/variety/cost/procurement policy, integer packages, utilized-versus-purchased separation, package surplus treatment, unsupported/indeterminate reporting and stable outcome classification.

### Architecture/component boundaries

Statically or structurally demonstrate inward dependencies, provider-owned cross-context contracts, no cross-context persistence access, no framework representations in inner public contracts, and no provider access during optimization.

### Coherent capture

Integration evidence must demonstrate that one planning input is internally coherent and that its provider read scope is closed before optimization.

### Optimization adapter

Demonstrate hard model infeasibility is distinct from timeout/unknown/numeric/technical failure; unproven feasible incumbents cannot become accepted primary plans; reportable values are independently recalculated.

### Persistence

Demonstrate authoritative decimals/time/currency/evidence states round-trip without semantic loss and ownership boundaries are preserved by migrations/schema.

### External interface

For identical explicit inputs and accepted provider state, canonical output is deterministic. Usage/technical failures cannot masquerade as accepted partial/no-plan outcomes.

## Acceptance gate

Implementation may be declared complete only when every applicable evidence class passes and Harness evaluates IMPLEMENTATION COMPLETE. Existing code or existing tests are not evidence for this redesign until an implementation revision is verified against this design.
