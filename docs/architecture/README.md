# Architecture

This directory owns accepted target architecture and technical constraints required to realize accepted requirements/domain semantics.

Current state: S3 Architecture is `PASS`; S4 implementation readiness is accepted through the canonical Harness `IMPLEMENTATION` consumer.

## Accepted target baseline

- [`target-architecture.md`](target-architecture.md) — accepted MVP realization structure, module boundaries, persistence/consistency rules and planning execution flow.
- [`ADR-008`](../decisions/ADR-008-mvp-modular-monolith-architecture.md) — modular monolith, context-aligned modules and one context-owned relational store.
- [`ADR-009`](../decisions/ADR-009-deterministic-planning-execution.md) — ephemeral immutable planning input snapshot, consistent-read coordination and in-process optimization-solver boundary.

The four accepted Bounded Contexts remain semantic ownership boundaries realized as logical modules inside one deployable process, not as network services.

Architecture follows accepted domain ownership rather than defining it retroactively. If later implementation evidence exposes missing product behavior or semantic ownership, reopen S1/S2; if it invalidates topology/consistency/technical contracts, reopen S3.


## Implementation-facing design

- [`../application/application-design.md`](../application/application-design.md) — use cases, application contracts and orchestration boundaries.
- [`../data/data-design.md`](../data/data-design.md) — persistence representation and migration contract.
- [`../interface/cli-contract.md`](../interface/cli-contract.md) — first-slice external CLI contract.
- [`../implementation/implementation-plan.md`](../implementation/implementation-plan.md) — ordered implementation slices.
- [`../implementation/completion-criteria.md`](../implementation/completion-criteria.md) — evidence required to claim implementation completion.
- [`ADR-010`](../decisions/ADR-010-first-implementation-stack.md) — concrete first-slice stack.
