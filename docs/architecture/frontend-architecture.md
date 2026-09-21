# Frontend Architecture

Status: accepted for the frontend design target.

Canonical UI inputs:
- `docs/interface/human-interface-design.md`;
- `docs/interface/frontend-presentation-system.yaml`;
- `docs/interface/frontend-screen-view-design.yaml`.

Architecture realizes these contracts without redefining visual hierarchy or screen composition.

## Runtime topology

The frontend extends the accepted modular monolith with one presentation adapter:

```
local browser
    |
loopback HTTP
    |
Web Presentation Adapter
    |
application contracts / composition
    |
existing bounded-context application + domain
    |
existing relational persistence / solver adapters
```

No new bounded context, service or database is introduced.

## Rendering model

Baseline rendering is server-side HTML.

Progressive JavaScript may improve disclosure, filtering, confirmation and focus behavior but cannot own business validation, optimization policy or authoritative domain state.

A page must remain semantically correct if presentation JavaScript fails; operations that inherently require form submission remain available through standard browser requests.

## Application boundary

The web adapter calls accepted application contracts only.

For overlapping operations, CLI and web adapters must converge on the same application commands/queries and therefore the same domain outcomes.

The web adapter may own:
- request parsing;
- route dispatch;
- anti-CSRF checks;
- view-model mapping;
- template rendering;
- flash/status presentation;
- presentation pagination/search/filter mechanics.

It may not own:
- nutrition-target derivation;
- evidence-state interpretation;
- offer executability;
- Purchase Plan outcome classification;
- solver status interpretation;
- coverage/variety/safety calculations.

## State ownership

### Server/domain state

Household/profile, Food Knowledge and Market Catalog facts remain provider-owned persisted state.

### Calculation state

A generated Purchase Plan is an application result and remains non-durable.

The HTTP response renders that result directly. The frontend does not add a saved-plan repository.

### Browser state

Allowed:
- form draft values before submission;
- disclosure/tab state;
- search/filter text;
- CSRF token/cookie;
- non-semantic navigation context.

Browser state is disposable and cannot establish product truth.

## Read/write patterns

- collection/detail pages use provider-owned query/application contracts;
- forms submit provider-owned commands;
- Generate Plan calls the existing `GeneratePurchasePlan` application use case;
- after successful persisted mutations, use Post/Redirect/Get to the owning detail/collection view;
- Generate Plan may return the non-durable result directly rather than inventing a durable result identifier.

## Error mapping

Presentation maps application/domain outcomes into explicit UI states.

At minimum distinguish:
- validation rejection;
- not found;
- conflict/stale input where exposed by provider command;
- accepted `partial`;
- accepted `no_executable_plan`;
- solver/technical failure;
- persistence/infrastructure failure.

HTTP status codes remain transport mechanics, not product semantics.

## Dependency direction

`web framework/templates -> frontend adapter -> application contracts -> domain`.

Domain/application packages have no dependency on web framework/template types.

Shared presentation helpers may contain only presentation semantics. They cannot become a generic business-service layer.

## Data volume/navigation

Collections may support server-side search/filter/pagination when data volume makes it useful, but this is an interface/query concern and does not change provider ownership.

No hard pagination size is canonicalized without evidence.

## Security

Consumes `docs/architecture/frontend-security.md`.

The frontend must remain loopback-only and CSRF protected until that Security Architecture is reopened.

## Quality/performance

Planning execution may be materially slower than ordinary CRUD because it includes optimization.

The request may render an in-progress state only if the chosen HTTP implementation can do so without introducing background job semantics. Otherwise the browser shows a submitting/busy state until the synchronous application call returns.

No background worker/job persistence is introduced.

## Reopening conditions

Reopen architecture before:
- separate frontend deployment;
- public JSON API;
- SPA-owned domain state;
- remote/multi-user hosting;
- background plan jobs;
- durable plan history;
- new database/store for UI state.

## Reliability and realization-quality contract

### Availability

The accepted frontend is a local single-process capability, not a highly available service. No availability percentage or multi-instance failover target is claimed. It is available only while the local application process and required provider database are available.

### Recovery

Recovery from ordinary process failure is process restart. Persisted provider-owned state remains in the accepted SQLite store; non-durable browser state and generated Purchase Plan results may be lost and are regenerated by the user. No background job, durable request queue or automatic work replay is introduced.

Startup fails closed when required configuration, database access or schema compatibility is invalid. Disaster-recovery RPO/RTO and backup policy are not invented by this frontend architecture and require a separate accepted requirement if material.

### Latency

Interactive CRUD/navigation is expected to behave as ordinary local interaction, while Generate Plan may be materially slower because it performs synchronous optimization. No numeric latency SLO is currently accepted. The synchronous request model is valid only while usability evidence does not require background-job semantics; unacceptable observed planning latency reopens Quality/System Architecture.

### Resource efficiency

The frontend adds one presentation adapter inside the existing process, no separate SPA runtime, worker fleet, durable job queue or plan-history store. Server rendering and view models must not duplicate authoritative domain state or retain completed plan results beyond the response lifecycle. No numeric CPU/memory budget is currently accepted; evidence of unbounded growth or a need for background concurrency reopens Quality/System Architecture.
