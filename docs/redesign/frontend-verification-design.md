# Frontend Verification Design

Status: accepted for the frontend design target.

Owner: REDESIGN-VERIFICATION.

## Purpose

Define evidence required to prove the user-facing frontend realizes accepted frontend requirements and upstream semantics.

## Presentation and screen-design evidence

Demonstrate:
- all six canonical screens inherit the shared Presentation System;
- shared hierarchy/status/form/collection/result patterns are used consistently unless an accepted local deviation exists;
- each screen realizes its required regions, states and responsive transformations;
- responsive realization preserves semantic order, labels and actions rather than only matching a visual snapshot.

## Evidence classes

### Journey evidence

Demonstrate:
- household member create/update journey, including provider-owned new-member identity creation distinct from profile replacement;
- catalog/manual market-data maintenance sufficient for accepted UI scope;
- Generate Purchase Plan with explicit dates/times;
- result interpretation for mapped-complete, partial and no-executable-plan outcomes.

### Semantic-state evidence

Demonstrate that UI preserves distinctions:
- missing vs zero;
- unsupported vs indeterminate;
- domain partial vs technical failure;
- no-executable-plan vs technical failure;
- safety diagnostic vs preferred target/individual guarantee;
- Base Food vs SKU vs Offer;
- purchased vs planned-utilized quantity vs surplus.

### Application-boundary evidence

Demonstrate that:
- web adapter calls provider/application contracts;
- Add Member invokes explicit `CreateMember` semantics and does not manufacture `member_id` or treat `SaveMemberProfile` as implicit identity creation;
- no domain calculation is reimplemented in route/template/JS code;
- no provider persistence or solver-native types cross the presentation boundary;
- CLI and web converge on the same application semantics for overlapping operations.

### Security evidence

Demonstrate:
- default listener binds only to loopback;
- non-accepted Host/origin/state-changing CSRF request is rejected before application mutation;
- no authentication/session credential subsystem exists in the local slice;
- untrusted rendered content is escaped by default;
- failed/unknown mutations do not render confirmed success.

### Non-durability evidence

Demonstrate:
- generated Purchase Plans are not written to a new plan-history table/store;
- browser/session state cannot become authoritative planning state.

### Accessibility/usability evidence

Demonstrate:
- all primary actions keyboard reachable;
- visible focus;
- form labels/error association;
- rejected forms expose an error summary with navigable field errors;
- asynchronous/status semantics, if any, are programmatically exposed;
- color is not the sole carrier of result/error meaning.

This is an engineering baseline, not a formal WCAG conformance claim.

### Responsive evidence

At minimum inspect/navigate the primary journeys at ordinary desktop and a narrow viewport without loss of information/actions.

No product mobile certification is implied.

## Test levels

- unit: view-model/error-mapping/presentation formatting/security helpers;
- component/template: rendered semantic structure and state variants;
- integration: HTTP adapter + real/fake application ports;
- browser journey: primary user flows through rendered UI;
- architecture/static: forbidden-dependency checks;
- security: Host/origin/CSRF and escaping checks.

## Acceptance gate

Frontend implementation is complete only when:
1. every required frontend test contract passes;
2. structural/security checks pass;
3. the frontend Harness consumer evaluates COMPLETE;
4. no unresolved Question blocks a required frontend capability.

## Traceability, data evidence and transition revalidation

### Requirement traceability

Every frontend verification obligation must trace to an accepted frontend requirement, upstream application/domain semantic, Security/Operability contract or structural design constraint. A passing browser test is not sufficient unless its oracle states which accepted behavior or constraint it proves.

### Data evidence

Frontend verification must demonstrate that presentation code neither creates a second authoritative data model nor changes accepted lifecycle semantics: provider writes go through application commands, generated plans remain non-durable, browser state is disposable, and data classification/redaction constraints are preserved at presentation/diagnostic boundaries.

### Functional evidence

The FUI contracts and journey evidence together prove the accepted user-visible operations and outcome distinctions for the selected frontend scope. Functional evidence includes success, validation rejection, accepted domain outcomes and technical failures rather than only happy-path navigation.

### Transition revalidation

Changes to frontend framework/runtime, application-contract shape, listener/security boundary, templates/rendering model or provider persistence compatibility re-run the affected frontend evidence classes before acceptance. Unchanged domain semantics need not be re-proven wholesale; revalidation follows the affected capability closure.
