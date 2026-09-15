# Nutrition Management repository agent map

## Purpose

This repository is the source of truth for the **Nutrition Management** product.

Conversation history is execution context, not project state. Consequential knowledge that must survive a session is promoted into the smallest correct repository owner.

## Startup

For non-trivial work:

1. read this file;
2. read the nearest scoped `AGENTS.md`;
3. load the smallest applicable Skill from `.agents/skills/`;
4. read only the canonical artifacts required by the task;
5. read `docs/plans/active/README.md` when current execution state, a lifecycle transition, blocker or authorization is relevant.

Do not preload the entire documentation tree.

## Source-of-truth map

- `docs/domain/` — living Strategic/Tactical DDD: meaning, identity, lifecycle, invariants and semantic ownership.
- `docs/requirements/` — accepted externally meaningful behavior and quality constraints.
- `docs/architecture/` — accepted target structure and runtime/consistency constraints.
- `docs/decisions/` — consequential decisions whose rationale must survive; accepted ADRs are superseded, not silently rewritten.
- `docs/plans/active/` — current execution state only.
- `docs/process/` — reusable working protocols; process is not product truth.
- `docs/baseline/` — explicit historical snapshots/provenance when a milestone snapshot is worth preserving; not the normal edit target.
- Git history — default archive for superseded working material and completed execution history.

When layers disagree materially, resolve the highest affected canonical owner first. Do not silently choose implementation behavior over accepted requirements/domain truth.

## Knowledge discipline

Classify consequential statements before using them as design truth:

- accepted/known;
- constraint;
- proposal;
- hypothesis;
- unknown;
- conflict.

A stakeholder statement is evidence. It becomes canonical product/domain truth only when accepted by the owning layer.

Never turn an unknown or proposal into accepted truth because it makes implementation easier.

Use `docs/process/decision-protocol.md` for missing/conflicting material answers and `docs/process/document-lifecycle.md` when creating, accepting, superseding or snapshotting durable project knowledge.

## DDD discipline

Use `docs/process/domain-change-protocol.md` when a requirement, design or implementation finding may change domain semantics.

A Bounded Context is a semantic ownership boundary. It is not automatically a service, database, package, screen, team or deployment unit.

Strategic DDD owns:
- ubiquitous-language boundaries;
- semantic responsibility and authority;
- Bounded Context boundaries and relationships;
- published semantic contracts.

Tactical DDD owns, inside an accepted context boundary:
- semantic identity;
- lifecycle;
- invariants and their owner;
- aggregate/entity/value-object distinctions when semantically justified;
- domain operations and facts.

Persistence schemas, ORM mappings, HTTP DTOs, framework classes, retries, deployment topology and similar realization choices belong downstream unless their concrete form is itself an accepted external contract.

## Architecture defaults

Until explicit ADRs say otherwise:

- prefer KISS and the smallest architecture that satisfies accepted requirements;
- preserve dependency direction toward domain policy;
- keep domain code free of transport, persistence, framework and DI-container concerns;
- use explicit ports at external seams when they add a real boundary;
- do not introduce distributed services, shared business-model packages or generic abstractions without demonstrated need.

These are repository design guardrails, not evidence that any particular Bounded Context, module or deployment unit already exists.

## Change lifecycle

For non-trivial product changes use `docs/process/change-lifecycle.md` and enter at the earliest affected layer:

```text
S0 Problem / Evidence
S1 Requirements
S2 Domain Design
S3 Architecture
S4 Implementation Readiness
-> Implementation
```

This is a reasoning/routing model, not a workflow engine. Do not create process machinery merely to mirror the stages.

## Change discipline

- Do not commit ordinary agent work directly to `main`; use a branch and PR.
- Keep one PR semantically coherent.
- Record accepted truth before relying on it downstream.
- Remove completed/superseded temporary planning artifacts when their durable outcomes have been absorbed; Git history is the archive.
- Run `make harness-check` after harness/process/routing changes.

## Review severity

- P0 — contradictory or impossible state; must be fixed.
- P1 — material semantic, ownership, architectural or correctness gap; must be fixed before the affected gate passes.
- P2 — worthwhile non-blocking improvement.
- P3 — cosmetic/local polish.
