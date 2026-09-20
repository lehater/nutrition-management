# Frontend Test Design

Status: accepted for the frontend design target.

Owner: TEST-DESIGN.

The contracts below define observable frontend behavior; concrete pytest/browser mechanics remain implementation.

## FUI-001 — Member profile validation

**Precondition:** Household exists.

**Operation:** submit member profile with a domain-invalid source fact.

**Oracle:**
- no successful mutation is reported;
- submitted values remain available for correction;
- field error and summary identify the rejection;
- focus/context permits reaching the rejected control;
- no derived target is fabricated client-side.

## FUI-002 — Member profile success

**Operation:** submit an accepted profile.

**Oracle:**
- provider command commits once;
- resulting member/profile is rendered from accepted application state;
- age/targets are not persisted/edited as independent source facts.

## FUI-003 — Unknown nutrient evidence

**Precondition:** Base Food nutrient evidence is non-quantitative/unknown.

**Oracle:**
- UI does not render it as numeric zero;
- evidence state remains visible;
- numeric editor behavior does not silently coerce it to zero.

## FUI-004 — Non-executable market product

**Precondition:** SKU lacks accepted edible-quantity conversion.

**Oracle:**
- SKU remains visible;
- UI marks it non-executable for planning;
- it is not silently presented as an executable Offer line.

## FUI-005 — Offer without explicit expiry

**Precondition:** Offer has observation timestamp but no `valid_until`.

**Oracle:**
- UI shows provenance/age;
- no fabricated expiry is displayed.

## FUI-006 — Plan input requires explicit semantic time

**Operation:** open Generate Plan.

**Oracle:**
- derivation date and market as-of are explicit controls;
- no current-clock semantic value is silently submitted.

## FUI-007 — mapped_complete result

**Precondition:** application returns mapped-complete plan with unsupported coverage.

**Oracle:**
- UI says mapped targets are covered;
- unsupported coverage remains visible;
- UI does not claim complete nutrition or individual safety.

## FUI-008 — partial result

**Precondition:** application returns executable partial plan.

**Oracle:**
- purchase groups/lines remain visible;
- material gaps/indeterminate/variety issues are explicit;
- partial is not rendered as technical error.

## FUI-009 — no executable plan

**Precondition:** application returns accepted `no_executable_plan`.

**Oracle:**
- no fake/empty successful basket is shown;
- domain outcome is distinct from infrastructure failure.

## FUI-010 — technical planning failure

**Precondition:** solver/application returns technical failure.

**Oracle:**
- no accepted plan is shown;
- technical retry/error semantics are distinct from `partial` and `no_executable_plan`.

## FUI-011 — purchase quantity distinctions

**Precondition:** selected line has package surplus.

**Oracle:** package count, purchased edible quantity, planned utilized quantity and surplus remain separately visible.

## FUI-012 — Purchase Group cost semantics

**Oracle:** group-level fee/threshold is displayed once at group level, not duplicated as line cost.

## FUI-013 — gap suggestions

**Precondition:** positive mapped gap has theoretical suggestions.

**Oracle:**
- suggestions are visibly theoretical;
- non-purchasable suggestion is not represented as a selected SKU/Offer;
- unsupported-applicability dimension receives no fabricated numeric gap suggestion.

## FUI-014 — stale browser result

**Operation:** view plan result, then change provider input elsewhere and return via browser history.

**Oracle:** UI does not assert old result is current; a new current result requires Generate Plan again.

## FUI-015 — CSRF

**Operation:** submit state-changing form without valid same-origin CSRF proof.

**Oracle:** request is rejected before application mutation.

## FUI-016 — Host/origin boundary

**Operation:** address local listener using disallowed Host/origin conditions.

**Oracle:** request is rejected according to Frontend Security Architecture.

## FUI-017 — template escaping

**Precondition:** stored human-readable text contains markup-like content.

**Oracle:** default rendering does not execute/inject it as active markup.

## FUI-018 — keyboard/focus

**Operation:** complete primary household -> plan journey using keyboard only, including one rejected form.

**Oracle:** every required action is reachable; focus remains visible; rejected control can be reached from error summary.

## FUI-019 — architecture boundary

**Static oracle:** web/templates do not import context persistence tables/repositories, solver adapter or domain-internal implementation types.

## FUI-020 — no durable plan history

**Integration oracle:** Generate Plan introduces no accepted persistence write for Purchase Plan/Planning Input history.
