# Architecture

This directory owns accepted target architecture and technical constraints required to realize accepted requirements/domain semantics.

Current state: S3 Architecture baseline is `proposed` and under review; implementation remains unauthorized.

## Current target baseline

- [`target-architecture.md`](target-architecture.md) — proposed MVP realization structure, module boundaries, persistence/consistency rules and planning execution flow.
- [`ADR-008`](../decisions/ADR-008-mvp-modular-monolith-architecture.md) — modular monolith, context-aligned modules and one context-owned relational store.
- [`ADR-009`](../decisions/ADR-009-deterministic-planning-execution.md) — immutable planning input snapshot and in-process optimization-solver boundary.

Repository guardrails in root `AGENTS.md` prefer KISS, inward dependency direction and explicit boundaries. The current proposal realizes the four accepted Bounded Contexts as logical modules, not services.

Architecture follows accepted domain ownership rather than defining it retroactively. If architecture review exposes missing product behavior or semantic ownership, S1/S2 must be reopened instead of hiding the gap in technical structure.
