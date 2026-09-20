# User-Facing Frontend Requirements

Status: accepted for the frontend design target.

## Purpose

Add a human-facing graphical interface for the accepted Nutrition Management MVP without changing its domain semantics or replacing the existing CLI.

The frontend is an additional presentation adapter over the accepted application layer.

## Required user outcomes

The frontend must let a local user:

- inspect the current household and its members;
- create and update the one current Nutrition Profile per member using the accepted profile fields;
- inspect the active Nutrition Standard Set identity/provenance used for target derivation;
- inspect and manually maintain the accepted Base Food, Product Card/SKU, Fulfilment Channel and Offer facts needed by the MVP;
- continue to use existing import mechanisms for bulk/reference-data acquisition; the first frontend slice does not need to reproduce every import workflow;
- generate one Purchase Plan using an explicit household, derivation date and market as-of instant;
- inspect the resulting purchase groups, package counts, utilized quantities, package surplus, costs and provenance;
- inspect mapped nutritional coverage and deviations;
- distinguish unsupported coverage from indeterminate nutrient evidence;
- inspect variety assessment and member-level safety diagnostics without implying individual allocation/safety guarantees;
- inspect theoretical Base Food suggestions for mapped positive nutrient gaps;
- distinguish `mapped_complete`, `partial`, `no_executable_plan` and technical failure.

## Interaction constraints

- User-visible terminology follows accepted domain language.
- Missing, unsupported, indeterminate and zero values must remain distinguishable.
- Safety limits must not be presented as preferred target maxima.
- A mapped-complete result must not be described as complete nutrition or an individual safety guarantee.
- Explicit semantic dates/times remain explicit; the frontend must not silently use the current clock for derivation date or market as-of.
- No durable Purchase Plan history, household inventory, consumption tracking, meal planning or member food allocation is introduced.
- The frontend must not allow direct editing of derived targets, calculated coverage, optimization decisions or provider provenance as if they were source facts.

## Channel scope

The accepted first frontend is a local browser interface.

It is intended for the same local single-user MVP deployment as the existing application. Remote/multi-user hosting, accounts and authentication are not product requirements of this slice.

## Quality baseline

The first frontend must remain usable without pointer-only interaction, expose visible focus, associate labels and validation errors with controls, and expose status changes semantically.

No formal accessibility-conformance level or mobile-specific product target is claimed by this requirement.
