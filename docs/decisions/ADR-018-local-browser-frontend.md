# ADR-018 — First user-facing frontend is a local browser adapter

Status: accepted for the frontend design target.

Date: 2026-09-20.

## Context

The accepted MVP currently exposes a deterministic CLI and explicitly avoids a network listener because no browser interface was previously required.

A new frontend design target now requires a graphical human interface while preserving the existing single-user local MVP, modular-monolith architecture and domain/application boundaries.

## Decision

Add a local browser presentation adapter with these constraints:

- it runs in the same deployable Python process as the existing modular monolith;
- it binds to loopback interfaces only by default;
- it is not a public/multi-user service;
- it introduces no account or authentication subsystem;
- it uses server-rendered HTML and ordinary HTML forms as the baseline;
- small progressive-enhancement JavaScript is allowed for presentation ergonomics only;
- no separate SPA backend/API contract is required;
- all business commands/queries call accepted application-layer contracts;
- browser/request representations never become domain/application contracts;
- CLI remains supported and semantically equivalent for overlapping operations.

The web adapter may add presentation-specific request/response/view models but may not duplicate product/domain policy.

## Security consequence

Introducing even a loopback HTTP listener creates a browser-origin boundary. State-changing browser requests therefore require explicit same-origin/CSRF protection and host/origin validation.

Remote binding requires a new Security/Architecture decision and is not permitted by this ADR.

## Data/result consequence

Purchase Plans remain non-durable. Rendering a result does not authorize persisted plan history or a browser-owned authoritative cache.

## Alternatives

### Separate SPA + JSON API

Deferred. It adds a second build/runtime boundary and public machine-interface design without a current need.

### Desktop GUI toolkit

Rejected for the first frontend slice. A local browser provides a simpler portable human interface while keeping one application process.

### CLI only

No longer sufficient for the selected frontend consumer, though it remains a supported adapter.
