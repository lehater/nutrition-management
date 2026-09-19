# ADR-016 — BLS 4.0 category assignment is an explicit exhaustive project registry

Status: `accepted` for the Harness pilot branch.

Date: 2026-09-19.
Lifecycle owner: `S2 Strategic/Tactical Domain Design / Food Knowledge classification semantics`.

## Context

ADR-005 defines the project top-level Food Category taxonomy for planning variety and explicitly rejects using BLS food-code groups as the project planning taxonomy.

The future BLS 4.0 production import contains 7,140 Base Foods. Every imported Base Food must have exactly one primary MVP top-level Food Category before it can enter canonical Food Knowledge.

The accepted BLS source artifacts provide source identity, names, nutrient composition and BLS-native classification structure, but they do not provide the project-specific DGE-aligned category assignment required by ADR-005.

Inferring the project category from a BLS code prefix, food name, nutrient profile or BLS-native grouping would therefore introduce an undocumented heuristic into canonical Food Knowledge.

## Decision

### Category assignment is explicit data

BLS 4.0 category membership is represented by a versioned project-owned registry keyed by exact BLS food code.

Each registry entry contains:

- exact BLS 4.0 food code;
- exactly one accepted ADR-005 top-level Food Category.

The registry is canonical Food Knowledge data for the BLS 4.0 source version.

### Coverage is exhaustive and exact

For the pinned BLS 4.0 source baseline:

- every one of the 7,140 distinct BLS food codes must occur exactly once in the category registry;
- no registry code may be absent from the pinned source;
- no source food may be missing from the registry;
- every category value must belong to the ADR-005 controlled top-level vocabulary.

Package generation fails closed on missing, duplicate, unknown or invalid assignments.

### No implicit fallback

`other_or_composite` is a normal explicit project category, not an automatic fallback.

A food is assigned `other_or_composite` only when the accepted classification explicitly chooses it. Unknown or difficult classification does not silently become `other_or_composite`.

### No heuristic derivation becomes canonical truth

BLS-native grouping, food-code structure, names, nutrient profiles or agent classification may be used as evidence or assistance while preparing the registry, but none of them independently determines the canonical category.

The accepted registry is the classification decision boundary.

### Version scope is explicit

The registry is specific to the pinned BLS 4.0 food-code set. A later BLS release requires explicit coverage review and a separately versioned registry state.

## Consequences

- category semantics remain aligned with ADR-005 rather than BLS source organization;
- import behavior is deterministic and reproducible;
- every imported Base Food has exactly one explicit project category;
- ambiguous classifications remain reviewable instead of becoming hidden parser heuristics;
- the production package can validate category coverage independently from nutrient normalization;
- agent assistance may accelerate classification without becoming the source of truth.

## Alternatives considered

### Derive category from BLS food-code group

Rejected because ADR-005 already rejects BLS grouping as the planning taxonomy and no accepted one-to-one semantic mapping exists.

### Classify by food name or nutrient profile during import

Rejected because classification would become heuristic, difficult to audit and sensitive to parser/model changes.

### Default unmapped foods to `other_or_composite`

Rejected because absence of a decision is not the same as an accepted composite-food classification.

### Store no category until later

Rejected because canonical Base Food semantics require exactly one primary top-level category.

## Supersession

Supersedes: none.
Superseded by: none.
