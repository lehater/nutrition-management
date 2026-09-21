# Component Design — Redesign Baseline

Status: accepted.

## Purpose

Fix architecturally significant implementation responsibilities and contracts without selecting language/framework/database/solver products.

## Component topology

```text
External Planning Adapter
        ↓
Generate Purchase Plan
        ↓
Planning Input Capture ─────→ provider application contracts
        ↓
immutable Planning Input
        ↓
Optimization Mechanism
        ↓
accepted solver-independent decision
        ↓
Plan Evaluation / Reporting
        ↓
Purchase Plan
        ↓ optional
Theoretical Gap Suggestions
```

Provider application contracts are owned by Nutrition Targeting, Food Knowledge and Market Catalog. Purchase Planning owns the shape required for its immutable planning input and its optimization/evaluation contracts.

## Nutrition Targeting

Public responsibilities:

- manage current household/member profile facts;
- manage versioned nutrition-standard facts and active version;
- derive member target for an explicit derivation date;
- aggregate compatible member demand while retaining unsupported applicability and safety provenance.

Persistence collaborators are consumer-shaped contracts owned by Nutrition Targeting application. Target derivation sees only the reads it needs; import/update commands see only their required writes.

Published planning contract contains immutable target facts/provenance, never persistence representations.

## Food Knowledge

Public responsibilities:

- manage canonical Base Food identity;
- normalize/preserve nutrient evidence and provenance;
- own category/material-representation semantics;
- publish canonical food facts;
- answer theoretical gap-candidate queries.

Commercial offer semantics are absent from this component boundary.

## Market Catalog

Public responsibilities:

- manage Product Card, edible package quantity, Merchant/Fulfilment Channel and Offer facts;
- validate product-specific nutrient overrides against Food Knowledge semantics;
- derive an executable market projection for an explicit as-of instant.

It consumes Food Knowledge through its published contract. It never writes Food Knowledge state.

## Purchase Planning

### Generate Purchase Plan

Orchestrates one run. It does not perform provider persistence, external parsing or solver-specific mechanics.

### Planning Input Source

Purchase Planning-owned contract that returns one immutable, internally coherent snapshot for explicit household, derivation date and market as-of inputs. Capture completes before optimization begins.

### Optimization Mechanism

Purchase Planning-owned behavioral contract accepting only the immutable planning input and returning a solver-independent decision or explicit technical/hard-infeasibility result. Representation may be a function, object or other language-native construct.

### Plan Evaluation / Reporting

Owns authoritative recalculation of coverage, variety, cost, outcome classification, uncertainty and provenance from accepted input + decision. Solver-native reported values are not authoritative product output.

### Gap Suggestion Source

Narrow advisory contract for theoretical food candidates. Suggestions occur after executable planning and cannot change basket selection or result classification.

## Composition boundary

The outer composition component selects concrete persistence, planning-input, optimization and gap-suggestion implementations. It may coordinate infrastructure across provider modules solely to realize the accepted coherent capture. It does not become a semantic owner.

## Mapping boundaries

- external/import representation → provider application command: adapter;
- persistence representation ↔ provider domain/application value: owning provider persistence adapter;
- provider published facts → Purchase Planning input values: planning-input adapter;
- planning input ↔ optimization-native representation: optimization adapter;
- application result → external representation: external adapter.

## Forbidden dependencies

- domain/application policy → persistence, solver or presentation frameworks;
- consumer context → provider persistence representation;
- optimization adapter → provider persistence/contracts during optimization;
- provider persistence → consumer domain model;
- external adapter → domain policy or datastore tables;
- shared generic repository/service/event bus introduced without accepted current need;
- durable Planning Input/Purchase Plan state introduced without an upstream requirement.

## Implementation freedoms

Language constructs, private helper decomposition, file/package layout below these public boundaries, dependency-construction technique and optimization library adapter shape remain implementation freedoms unless fixed by Implementation Design.

No coding agent may change semantic ownership, provider/consumer direction, coherent-capture semantics, outcome/failure semantics or introduce a new integration mechanism without reopening design.

## Testability contract

Component boundaries must permit verification without replacing accepted semantics.

- application use cases depend on narrow ports/provider contracts that can be substituted by deterministic fakes in tests;
- domain policy is testable without database, solver, CLI/web framework or Harness runtime;
- persistence, solver and external adapters can be exercised independently against their owned contracts;
- composition is the only place that binds concrete adapters, so integration tests can replace a dependency without changing use-case code;
- time/version inputs that affect semantics are explicit inputs, not hidden globals;
- no test-only public production API is introduced solely to reach private implementation details.

A component decomposition that requires end-to-end infrastructure to verify ordinary domain/application behavior fails this design obligation and must be revised before coding.
