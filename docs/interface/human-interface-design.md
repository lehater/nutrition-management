# Human Interface Design — Nutrition Management Frontend

Status: accepted for the frontend design target.

Owner: INTERFACE-DESIGN.

## Information architecture

Primary locations:

1. **Overview**
2. **Household**
3. **Food Knowledge**
4. **Market**
5. **Plan**

The primary path is:

`Household / data readiness -> Plan -> Result`.

Administrative catalog work remains reachable but does not dominate the planning journey.

## Global shell

Persistent shell provides:
- product title;
- primary navigation;
- current location;
- non-modal status region for operation completion/failure;
- no account/profile controls because the local MVP has no authentication/account model.

Technical identifiers may be inspectable where useful, but human-readable domain meaning leads.

## Overview

Purpose: show readiness for the primary journey without inventing a universal readiness score.

Show:
- household/member count and profile issues that block accepted derivation;
- active Nutrition Standard Set identity;
- presence of Food Knowledge and executable Market data;
- direct action to Generate Plan.

Do not label the system “ready” merely because records exist; only concrete missing/invalid conditions are reported.

## Household workspace

### Household view

Shows:
- members;
- current profile summary;
- explicit unresolved/applicability-relevant facts when accepted semantics expose them.

Actions:
- add member;
- edit current profile;
- generate plan for this household.

### Member form

Fields follow accepted Nutrition Profile source facts:
- date of birth;
- sex applicability input;
- height;
- current weight;
- current-weight date;
- PAL when required;
- optional target weight;
- optional target date.

UI rules:
- never ask for separately entered age/development stage;
- do not infer phytate/menstruation/menopause/pregnancy/lactation inputs;
- do not silently clamp/default PAL;
- validation errors remain attached to the relevant field plus an accessible summary.

States:
`loading | loaded | submitting | validation-rejected | saved | technical-failure`.

## Food Knowledge workspace

### Base Food collection

Supports browse/search by human-readable name/category. Search is interface convenience and not a new domain query semantic.

Shows:
- Base Food name/identity;
- top-level category;
- source/provenance summary;
- evidence completeness indicator that never collapses unknown/trace to zero.

Actions:
- create manual Base Food;
- open detail.

### Base Food detail/editor

Shows/edits accepted source facts:
- name;
- category;
- provenance;
- canonical nutrient facts/evidence state.

Rules:
- evidence states remain explicit;
- numeric amount is enabled only for quantitative evidence states accepted upstream;
- units/basis follow canonical Food Knowledge semantics;
- product/offer fields do not appear here.

## Market workspace

Sub-locations:
- Products;
- Fulfilment Channels;
- Offers.

### Product Card/SKU

Shows/edits:
- product identity/name;
- Base Food reference;
- package quantity;
- edible-quantity conversion required by accepted semantics;
- product-specific normalized nutrient overrides where supported.

A Product that lacks executable edible quantity remains visible but is marked non-executable for planning.

### Fulfilment Channel

Shows/edits:
- Merchant;
- pickup/delivery mode;
- currency/context;
- minimum order;
- fixed fulfilment/delivery fee;
- optional free-delivery threshold;
- condition observation/validity provenance.

### Offer

Shows/edits:
- SKU;
- Fulfilment Channel;
- price/currency;
- availability state;
- observed-at;
- valid-from/valid-until when supplied.

UI never invents an expiry for a missing `valid_until`.

## Plan workspace

Input:
- household;
- explicit derivation date;
- explicit market as-of instant.

Before submit, show a concise summary:
- household/member count;
- active standard version;
- currently visible catalog/market warnings;
- explicit dates/times.

States:
- editing;
- submitting;
- result;
- no-executable-plan;
- validation-rejected;
- technical-failure.

No current-time semantic default is inserted.

## Plan result

Result is one interaction context with sections/tabs that preserve the same semantic object; exact tab/accordion implementation is free.

### Summary

Shows:
- outcome: `mapped_complete | partial | no_executable_plan`;
- total acquisition cost/currency when a plan exists;
- Purchase Group and Merchant counts;
- concise warning count for unsupported/indeterminate/safety diagnostics.

Language rules:
- `mapped_complete` is “Mapped targets covered” rather than “Nutrition complete”;
- safety diagnostics are advisory and never claim member allocation safety.

### Purchase groups

Group by Fulfilment Channel.

For every selected line show:
- SKU/Base Food;
- package count;
- purchased edible quantity;
- planned utilized quantity;
- package surplus;
- line cost;
- Offer observation/validity provenance.

Group-level fulfilment fees/thresholds appear once per group.

### Nutrition coverage

Each active dimension is rendered in exactly one appropriate semantic class:
- mapped/determinate assessment;
- unsupported applicability/mapping;
- indeterminate food evidence.

Show target semantic kind and direction/range where material. Do not convert unsupported/indeterminate into zero.

### Variety

Show accepted category count, Base Food count and concentration assessment from planned utilized quantity.

### Safety diagnostics

Keep separate from adequacy. Explain that aggregate plan evidence cannot prove individual intake/allocation safety.

### Gaps and suggestions

For positive mapped gaps show:
- missing nutrient measure;
- material deviation;
- theoretical Base Food suggestions with category/provenance;
- clear distinction that a theoretical suggestion is not necessarily purchasable.

No suggestions are shown for unsupported-applicability dimensions without a numeric target.

### Provenance

Expose:
- Nutrition Standard version/derivation date;
- market as-of;
- offer observation/validity;
- relevant data source provenance.

## Global state semantics

Never collapse:
- loading into empty;
- missing into zero;
- unsupported into satisfied;
- indeterminate into failed;
- domain `partial` into technical failure;
- `no_executable_plan` into technical failure;
- stale browser content into current plan truth.

## Keyboard/focus/accessibility baseline

- semantic HTML elements are preferred over custom controls;
- all actions are keyboard reachable;
- visible focus is always present;
- form labels and errors are programmatically associated;
- submit/result/error status changes are exposed through semantic status regions;
- focus moves to an error summary after rejected submission and can navigate to invalid controls;
- information is not encoded by color alone.

No formal WCAG conformance claim is made by this artifact.

## Responsive behavior

Primary target is an ordinary desktop/laptop browser. Narrow layouts must reflow without losing information or actions, but no mobile-specific workflow or breakpoint contract is introduced.

## Deliberately unconstrained

- CSS framework/component library;
- exact typography/colors/spacing;
- table versus responsive card realization where semantics remain equivalent;
- JS framework;
- exact route strings;
- modal versus dedicated page for simple create/edit tasks.
