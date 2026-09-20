# Frontend Architecture

Status: accepted for the frontend design target.

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
