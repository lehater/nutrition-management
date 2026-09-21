# User-Facing Frontend Requirements

Status: accepted for the frontend design target.

## Purpose

Add a human-facing graphical interface for the accepted Nutrition Management MVP without changing its domain semantics or replacing the existing CLI.

The frontend is an additional presentation adapter over the accepted application layer.

## Required user outcomes

The frontend must let a local user:

- [FR-HOUSEHOLD-001] inspect the current household and its members;
- [FR-PROFILE-001] create and update the one current Nutrition Profile per member using the accepted profile fields;
- [FR-STANDARD-001] inspect the active Nutrition Standard Set identity/provenance used for target derivation;
- [FR-CATALOG-001] inspect and manually maintain the accepted Base Food, Product Card/SKU, Fulfilment Channel and Offer facts needed by the MVP;
- [FR-IMPORT-001] continue to use existing import mechanisms for bulk/reference-data acquisition; the first frontend slice does not need to reproduce every import workflow;
- [FR-PLAN-001] generate one Purchase Plan using an explicit household, derivation date and market as-of instant;
- [FR-RESULT-001] inspect the resulting purchase groups, package counts, utilized quantities, package surplus, costs and provenance;
- [FR-COVERAGE-001] inspect mapped nutritional coverage and deviations;
- [FR-EVIDENCE-001] distinguish unsupported coverage from indeterminate nutrient evidence;
- [FR-SAFETY-001] inspect variety assessment and member-level safety diagnostics without implying individual allocation/safety guarantees;
- [FR-SUGGESTION-001] inspect theoretical Base Food suggestions for mapped positive nutrient gaps;
- [FR-OUTCOME-001] distinguish `mapped_complete`, `partial`, `no_executable_plan` and technical failure.

## Interaction constraints

- [FR-SEMANTICS-001] User-visible terminology follows accepted domain language.
- [FR-SEMANTICS-002] Missing, unsupported, indeterminate and zero values must remain distinguishable.
- [FR-SAFETY-002] Safety limits must not be presented as preferred target maxima.
- [FR-COMPLETENESS-001] A mapped-complete result must not be described as complete nutrition or an individual safety guarantee.
- [FR-TIME-001] Explicit semantic dates/times remain explicit; the frontend must not silently use the current clock for derivation date or market as-of.
- [FR-SCOPE-001] No durable Purchase Plan history, household inventory, consumption tracking, meal planning or member food allocation is introduced.
- [FR-AUTHORITY-001] The frontend must not allow direct editing of derived targets, calculated coverage, optimization decisions or provider provenance as if they were source facts.

## Channel scope

- [FR-CHANNEL-001] The accepted first frontend is a local browser interface.
- [FR-CHANNEL-002] It is intended for the same local single-user MVP deployment as the existing application; remote/multi-user hosting, accounts and authentication are not product requirements of this slice.

## Quality baseline

- [FR-QUALITY-001] The first frontend must remain usable without pointer-only interaction, expose visible focus, associate labels and validation errors with controls, and expose status changes semantically.
- [FR-QUALITY-002] No formal accessibility-conformance level or mobile-specific product target is required for this slice.
