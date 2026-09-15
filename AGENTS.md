# Nutrition Management repository agent map

## Purpose

This repository is the source of truth for the **Nutrition Management** product.

Conversation history is execution context, not project state. Durable product knowledge and resumable execution state belong in this repository.

## Startup

For non-trivial work:
1. read this file;
2. read the nearest scoped `AGENTS.md` for the area being changed;
3. read only the canonical project artifacts required by the task;
4. read `docs/plans/active/README.md` only when current execution state, blockers or authorization are relevant.

Do not preload the entire documentation tree.

## Source-of-truth map

- `docs/problem.md` — accepted problem/outcome, relevant evidence and scope assumptions.
- `docs/requirements/` — accepted externally meaningful behavior and quality constraints.
- `docs/domain/` — living domain semantics, identity, lifecycle, invariants and semantic ownership.
- `docs/architecture/` — accepted target structure and runtime/consistency constraints.
- `docs/decisions/` — consequential project decisions and rationale.
- `docs/plans/active/` — current execution state only.
- `docs/baseline/` — explicit historical snapshots/provenance when worth retaining; not living truth.
- Git history — default archive for superseded working material and completed execution history.

When project truth layers disagree materially, resolve the highest affected canonical owner first rather than silently choosing downstream implementation behavior.

## Project architecture guardrails

Until explicit project ADRs say otherwise:
- prefer KISS and the smallest architecture that satisfies accepted requirements;
- preserve dependency direction toward domain policy;
- keep domain code free of transport, persistence, framework and DI-container concerns;
- use explicit ports at external seams when they add a real boundary;
- do not introduce distributed services, shared business-model packages or generic abstractions without demonstrated need.

A Bounded Context is a semantic ownership boundary, not automatically a service, database, package, screen, team or deployment unit.

## Change discipline

- Do not commit ordinary agent work directly to `main`; use a branch and PR.
- Keep one PR semantically coherent.
- Record accepted project truth in its owning artifact before relying on it downstream.
- Remove completed temporary planning/discovery material once durable outcomes have been absorbed; Git history is the archive.
