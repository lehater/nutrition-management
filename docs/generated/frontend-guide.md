# Frontend Design Guide

> Generated human-readable projection. Canonical truth remains in the referenced project artifacts and Harness graphs.

## Frontend target

Nutrition Management gains an additional local browser interface over the accepted MVP application layer. The existing CLI remains supported.

The frontend does not introduce new nutrition, market or optimization semantics.

Canonical sources:
- `docs/requirements/frontend-requirements.md`;
- `docs/application/user-journeys.md`;
- `docs/application/frontend-application-contracts.md`;
- `docs/interface/human-interface-design.md`;
- `docs/decisions/ADR-018-local-browser-frontend.md`;
- `docs/architecture/frontend-security.md`;
- `docs/architecture/frontend-architecture.md`.

## Primary user flow

1. maintain household/member profile source facts;
2. prepare/inspect Food Knowledge and Market data;
3. open Plan;
4. select household and explicit derivation/market times;
5. generate the accepted Purchase Plan;
6. inspect basket/cost, mapped coverage, unsupported/indeterminate dimensions, variety, safety diagnostics, gap suggestions and provenance.

The result is not saved as durable plan history.

## Main screens

- Overview — concrete data/readiness signals and direct Plan action.
- Household — members and current profile forms.
- Food Knowledge — Base Foods, categories, nutrient evidence and provenance.
- Market — Products/SKUs, Fulfilment Channels and Offers.
- Plan — explicit calculation inputs.
- Plan Result — summary, purchase groups, nutrition coverage, variety, safety, gaps/suggestions and provenance.

## Important UI semantics

The UI must preserve:
- missing != zero;
- unsupported != indeterminate;
- partial != technical failure;
- no executable plan != technical failure;
- Base Food != SKU != Offer;
- purchased quantity != planned utilized quantity != package surplus;
- safety diagnostics != individual safety guarantee.

`mapped_complete` is presented only as coverage of the quantitatively resolved/mapped target subset.

## Runtime design

The first frontend is server-rendered:
- same Python modular-monolith process;
- loopback-only local HTTP;
- Starlette + Uvicorn + Jinja2;
- ordinary HTML forms;
- minimal optional JavaScript;
- no SPA/public JSON API;
- no authentication/account system;
- CSRF + host/origin protection for the browser boundary.

## Code boundary

Presentation code may parse requests, map application results and render HTML. Provider reads and mutations use the accepted contracts in `docs/application/frontend-application-contracts.md`.

It must not:
- query context persistence directly;
- call solver internals;
- recalculate nutrition/coverage/offer executability;
- persist plan history;
- introduce a browser-owned business state model.

## Verification

Canonical evidence/test design:
- `docs/redesign/frontend-verification-design.md`;
- `docs/redesign/frontend-test-design.md`;
- `docs/redesign/frontend-component-design.md`;
- `docs/redesign/frontend-implementation-design.md`.

Harness target: `FRONTEND-IMPLEMENTATION`.
