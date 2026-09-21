# ADR-016 — BLS 4.0 category assignment is an explicit exhaustive project decision registry

Status: `accepted` for the current canonical project baseline.

Date: 2026-09-19.
Lifecycle owner: `S2 Strategic/Tactical Domain Design / Food Knowledge classification semantics`.

## Context

ADR-005 defines the project top-level Food Category taxonomy for planning variety and explicitly rejects using BLS food groups directly as the project planning taxonomy.

The future BLS 4.0 production import contains 7,140 Base Foods. Every imported Base Food must resolve to exactly one primary MVP top-level Food Category before it can enter canonical Food Knowledge.

BLS codes are hierarchical and their source-native groups are useful classification evidence, but those groups are not themselves the project taxonomy. Import-time inference from a code prefix, display name or nutrient profile would hide project classification decisions inside parser behavior.

A literal 7,140-row project table is sufficient but unnecessarily duplicates classification decisions when a reviewed source-code prefix has one accepted project meaning for every covered code.

## Decision

### Category assignment is explicit project data

BLS 4.0 category membership is governed by a versioned project-owned decision registry.

The registry may contain:

- explicit BLS code-prefix rules where the whole covered source subset has one accepted ADR-005 category;
- exact-code overrides for exceptions or cases that require narrower decisions.

Rules and overrides are canonical Food Knowledge data. They are not parser heuristics.

### Resolution semantics are deterministic

For a pinned BLS 4.0 source code:

1. an exact-code override, when present, is authoritative for that code;
2. otherwise exactly one prefix rule must match;
3. zero matching rules is an unmapped source food;
4. more than one matching prefix rule is invalid configuration rather than an implicit precedence rule.

Prefix rules therefore must be non-overlapping for source codes that do not have an exact override.

### Coverage is exhaustive against the pinned source set

Validation evaluates the registry against the exact pinned BLS 4.0 source-code set.

For all 7,140 distinct source codes:

- every source code resolves to exactly one accepted ADR-005 top-level Food Category;
- every exact override references an existing source code;
- every prefix rule matches at least one source code;
- no source code remains unmapped;
- no invalid category value is accepted.

The materialized per-code mapping is a deterministic projection of the canonical decision registry and may be emitted into the normalized production package.

### No implicit fallback

`other_or_composite` is a normal explicit project category, not an automatic fallback.

A rule or exact override may assign it explicitly. Absence of a classification decision never becomes `other_or_composite` automatically.

### Evidence does not become authority

BLS-native grouping, code hierarchy, names, nutrient profiles or agent/model suggestions may be used as evidence while preparing rules and overrides.

They do not independently determine the project category. The reviewed registry is the classification decision boundary.

### Version scope is explicit

The registry is specific to the pinned BLS 4.0 source-code set. A later BLS release requires explicit coverage review and a separately accepted registry state.

## Consequences

- project category semantics remain aligned with ADR-005 rather than BLS source organization;
- repeated classification decisions can be represented once as explicit reviewed prefix rules;
- exceptions remain visible as exact-code overrides;
- package generation can deterministically materialize a complete 7,140-row mapping;
- exact coverage remains independently verifiable against pinned source identity;
- ambiguous classifications cannot disappear into parser code or an implicit fallback;
- agent assistance may propose candidate rules/overrides without becoming the source of truth.

## Alternatives considered

### Store exactly 7,140 manually repeated rows as canonical truth

Rejected as the only allowed representation because it duplicates identical reviewed decisions and makes review unnecessarily noisy. A materialized 7,140-row projection remains valid package output.

### Derive category directly from BLS food-code group at import time

Rejected because ADR-005 does not adopt the BLS grouping as project taxonomy. Source hierarchy is evidence for explicit project rules, not authority.

### Classify by food name or nutrient profile during import

Rejected because classification would become heuristic, difficult to audit and sensitive to parser/model changes.

### Default unmapped foods to `other_or_composite`

Rejected because absence of a decision is not the same as an accepted composite-food classification.

## Supersession

Supersedes: none.
Superseded by: none.
