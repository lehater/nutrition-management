# MVP Implementation Plan

Status: accepted for implementation readiness.

## Goal

Realize the accepted Nutrition Management MVP as one Python modular monolith without inventing product, domain, architecture, interface or persistence semantics during coding.

## Inputs

Implementation is governed by:

- accepted product requirements and domain/context contracts;
- target architecture and ADR-008/009;
- application design;
- data design;
- CLI contract;
- ADR-010 implementation stack;
- verification strategy.

If implementation exposes a contradiction in these inputs, create an upstream design Question instead of resolving it implicitly in code.

## Slice 1 — executable project skeleton

Establish the locked Python 3.14 project, context-aligned package boundaries, composition root, file-backed SQLite configuration, Alembic migration execution and CLI entry point.

Exit evidence: package imports, migration/bootstrap and architecture-boundary tests pass.

## Slice 2 — Nutrition Targeting provider

Implement member/standard persistence, source-data loading, target derivation, safety/reference semantics and the published household-target application contract.

Exit evidence: targeting unit/application tests cover derivation date, standard version/provenance, supported and unsupported mappings, and safety evidence.

## Slice 3 — Food Knowledge provider

Implement Base Food/nutrient evidence persistence, canonical evidence-state semantics, category/provenance representation and theoretical gap-candidate queries.

Exit evidence: evidence states remain distinct; only quantitative states carry numeric amounts; provider contract tests pass.

## Slice 4 — Market Catalog provider

Implement SKU/package representation, normalized nutrient overrides, channels/offers and explicit market-time executability.

Exit evidence: package edible quantity, currency, availability, observed/valid time and order conditions are preserved through the published executable-offer contract.

## Slice 5 — coherent planning snapshot

Compose provider contracts under one database-consistent read scope into an immutable Planning Input Snapshot, then close the read scope before optimization.

Exit evidence: integration tests demonstrate one coherent capture and prohibit provider persistence access during solver execution.

## Slice 6 — Purchase Planning policy and solver adapter

Implement solver-independent planning model construction, SCIP adapter, sequential ADR-007 objective stages, hard infeasibility mapping, deterministic final technical tie order and post-solve recalculation.

Exit evidence: policy-optimal and hard-model-infeasible paths are distinct from timeout/unknown/error; feasible unfinished incumbents cannot become primary plans.

## Slice 7 — reporting and theoretical gap enrichment

Produce canonical Purchase Plan coverage/cost/variety/provenance diagnostics and request theoretical Food Knowledge suggestions only after executable optimization.

Exit evidence: suggestions cannot change basket selection/outcome classification; unknown nutrient evidence cannot become satisfied coverage.

## Slice 8 — CLI end-to-end path

Wire the accepted CLI arguments to composition and `GeneratePurchasePlan`; emit deterministic canonical JSON.

Exit evidence: representative file-backed database fixture produces a repeatable end-to-end result for identical explicit inputs.

## Slice 9 — implementation acceptance

Run the complete verification strategy, migration/data-integrity checks, architecture-boundary tests and end-to-end planning test.

No implementation slice is complete merely because code exists. Its accepted exit evidence must pass.

## Change discipline

Coding may choose local names, helper functions and private decomposition where these do not alter accepted public/semantic contracts.

The following require reopening upstream design:

- a new Bounded Context or changed ownership direction;
- direct cross-context persistence access;
- new durable product state;
- a new external interaction contract;
- changed target/evidence/offer/planning semantics;
- asynchronous/distributed execution;
- solver behavior that weakens deterministic policy completion;
- persistence behavior that cannot provide the accepted coherent-read boundary.
