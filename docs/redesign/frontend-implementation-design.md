# Frontend Implementation Design

Status: accepted terminal pre-code design for the frontend target.

Owner: IMPLEMENTATION-DESIGN.

## Selected realization

Extend the current Python 3.14 modular-monolith process with:

- Starlette as the minimal HTTP/routing layer;
- Uvicorn as the local ASGI server;
- Jinja2 server-rendered templates;
- ordinary HTML forms;
- minimal framework-free JavaScript only for progressive presentation enhancement;
- existing SQLAlchemy Core/Alembic/SQLite/PySCIPOpt implementation unchanged behind application contracts;
- pytest for unit/integration tests;
- browser-level tests using Playwright.

The existing deterministic CLI remains supported.

## Why this realization

It adds the smallest practical browser surface without:
- creating a separate Node/SPA project;
- requiring a public JSON API;
- duplicating application policy in TypeScript/browser state;
- creating another deployable/service.

## Package realization

Add presentation-only modules beneath the existing top-level package, conceptually:

```
presentation/
  web/
    app.py
    routes/
      overview.py
      household.py
      food_knowledge.py
      market.py
      planning.py
    view_models/
    forms/
    security/
    templates/
    static/
```

Exact private file names may vary, but feature ownership and dependency direction from Component Design must remain.

## Application prerequisites

Before implementing a route, the corresponding provider application command/query must exist as an accepted narrow contract.

If implementation finds that a required manual UI operation lacks an application contract, stop that slice and reopen APPLICATION-DESIGN/owning context rather than writing directly to repositories.

## Server configuration

Default:
- loopback bind only;
- explicit configurable local port;
- no automatic remote bind;
- no authentication subsystem.

State-changing routes enforce Frontend Security Architecture before application dispatch.

## Rendering

- Jinja2 autoescaping enabled;
- templates consume explicit view models only;
- domain/persistence/solver objects are not passed wholesale;
- server rendering owns initial/authoritative result representation;
- JavaScript may enhance disclosure/search ergonomics but is not required for business correctness.

## Forms

Use explicit parsing/mapping per feature.

Do not introduce a generic CRUD/form framework spanning bounded contexts.

All domain/application validation remains authoritative. Presentation validation may improve feedback but cannot replace server-side application/domain checks.

## Planning request

`POST /planning/generate` invokes `GeneratePurchasePlan` synchronously for the first slice and renders the non-durable result response.

No job queue, polling protocol, saved result id or plan-history persistence is introduced.

If synchronous solver latency later becomes unacceptable, that is an Architecture/Quality reopening condition.

## Dependencies

Add direct dependencies only as required by the frontend:
- Starlette;
- Uvicorn;
- Jinja2;
- Playwright test tooling as development/test dependency.

Pin exact resolved versions through the existing uv lockfile.

## Verification

Implementation must realize `docs/redesign/frontend-test-design.md` and `docs/redesign/frontend-verification-design.md`.

## Implementation slices

1. web composition, loopback/security shell, template base and structural tests;
2. Overview + Household/member management;
3. Food Knowledge read/manual-edit surface;
4. Market Product/Channel/Offer surface;
5. Plan form and GeneratePurchasePlan integration;
6. full Plan Result semantic presentation;
7. keyboard/focus/narrow-layout hardening;
8. browser/security/architecture verification;
9. generated human documentation refresh.

Each slice must use accepted application contracts and must not read/write provider persistence directly.

## Coding decisions that remain free

- private helper names;
- template macro decomposition;
- CSS class naming;
- small visual token values;
- exact route-controller function structure;
- test helper organization.

## Coding decisions that are not free

Coding must not:
- add a separate SPA/API;
- widen listener binding;
- invent authentication;
- persist Purchase Plans;
- add business calculations to browser/routes/templates;
- collapse unsupported/indeterminate/zero semantics;
- add new domain fields/workflows;
- bypass provider application contracts.

Any such need reopens its owning design artifact.
