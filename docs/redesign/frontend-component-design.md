# Frontend Component Design

Status: accepted for the frontend design target.

Owner: COMPONENT-DESIGN.

## Purpose

Define implementation-facing frontend responsibilities without moving product/domain policy into the presentation layer.

## Topology

```
Web composition
  ├─ shell/navigation
  ├─ household feature
  ├─ food-knowledge feature
  ├─ market feature
  └─ planning feature
        ↓
presentation/application mappers
        ↓
provider-owned application contracts
        ↓
accepted domain/application implementation
```

## Web composition

Responsibilities:
- construct the web application and route table;
- inject accepted application commands/queries;
- configure template environment and presentation-security helpers;
- own no business policy.

## Shared presentation components

Allowed shared responsibilities:
- page shell/navigation;
- semantic form/error summary rendering;
- status messages;
- money/decimal/date/time formatting;
- opaque-id display/copy helpers;
- pagination/search presentation;
- reusable table/detail primitives;
- CSRF presentation integration.

Forbidden:
- nutrient evidence interpretation;
- offer executability logic;
- plan outcome classification;
- domain validation;
- cross-feature mutable global store.

## Household feature

Owns presentation controllers/view models for:
- household/member collection/detail;
- member create/edit form;
- profile validation mapping.

Depends on Nutrition Targeting application contracts.

It must not calculate age, target nutrients, PAL policy or derived nutrition targets itself.

## Food Knowledge feature

Owns presentation controllers/view models for:
- Base Food list/detail/edit;
- category/provenance presentation;
- nutrient evidence editing/display.

Depends on Food Knowledge application contracts.

A presentation view model may flatten data for rendering but may not reinterpret evidence states or nutrient basis.

## Market feature

Owns presentation controllers/view models for:
- Product Cards/SKUs;
- Fulfilment Channels;
- Offers;
- executability diagnostics exposed by accepted application semantics.

Depends on Market Catalog application contracts and provider-owned Food Knowledge references where exposed through accepted contracts.

It must not query Food Knowledge persistence directly.

## Planning feature

Owns:
- Generate Plan form;
- synchronous invocation of `GeneratePurchasePlan`;
- mapping accepted Purchase Plan result into presentation sections;
- non-durable result page.

Presentation view models:
- PlanSummaryView;
- PurchaseGroupView;
- PlanLineView;
- CoverageDimensionView;
- VarietyView;
- SafetyDiagnosticView;
- GapSuggestionView;
- ProvenanceView.

These types are presentation projections and never cross into domain/application as inputs.

## Web security components

### LocalHostGuard

Rejects non-accepted Host/bind configuration before domain/application dispatch.

### CsrfProtection

Owns process-local presentation CSRF token issuance/validation.

It has no user identity/authorization semantics.

### SafeTemplateEnvironment

Escapes untrusted content by default and exposes only explicit formatting helpers.

## Mapping boundaries

- browser strings/files -> web request model;
- web request model -> application command/query input;
- application/domain rejection -> field/global presentation errors;
- application result -> immutable page view model;
- view model -> HTML template.

No template consumes persistence rows, solver-native objects or framework-specific domain wrappers.

## Dependency rules

Allowed:
`templates/routes -> feature controller -> application contract`.

Forbidden:
- domain/application -> web framework/template;
- web feature -> provider database tables/repositories;
- one feature importing another feature's private controllers/view models;
- web feature -> solver adapter;
- generic `services` module that accumulates domain decisions;
- browser JS becoming an alternate application layer.

## Route realization

Routes are adapter-owned mechanics.

Suggested implementation map:
- `GET /` overview;
- `GET /households/{household_id}`;
- `GET|POST /households/{household_id}/members/new`;
- `GET|POST /households/{household_id}/members/{member_id}`;
- `GET|POST /foods...`;
- `GET|POST /market/products...`;
- `GET|POST /market/channels...`;
- `GET|POST /market/offers...`;
- `GET /planning`;
- `POST /planning/generate`.

Exact route spelling remains adapter implementation detail unless tests or links intentionally make it a supported contract.

## Structural verification

Tests/static checks must demonstrate:
- web dependencies point inward only;
- templates/controllers do not import persistence or solver modules;
- each feature depends on narrow application-facing contracts;
- planning presentation cannot construct accepted Purchase Plan facts itself;
- browser-specific security is confined to presentation infrastructure.

## Maintainability and testability contract

The frontend decomposition must remain independently understandable, modifiable and testable:

- feature controllers/view models remain cohesive by user-facing area and do not share private mutable state;
- shared presentation helpers contain only presentation semantics and have narrow, named contracts;
- application dependencies are injected through accepted commands/queries so feature behavior can be tested with deterministic fakes;
- templates/view-model mapping can be tested without a live database or solver;
- web security helpers can be tested independently from domain behavior;
- a change isolated to one feature must not require unrelated feature-controller changes unless a shared public presentation contract changes;
- architecture/static tests enforce forbidden dependencies so accidental coupling is detected mechanically.

A frontend design that requires a live end-to-end stack to verify ordinary view-model, route-mapping or presentation-state behavior is not implementation-ready.
