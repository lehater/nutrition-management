# Full Design Revalidation Record

Status: accepted.

## Problem and MVP

The core problem remains valid: produce an actionable 30-day household purchase recommendation that balances nutrition, variety, acquisition cost and procurement simplicity while preserving uncertainty/provenance.

The MVP boundary remains intentionally advisory. It does not claim individual allocation feasibility, actual consumption, therapeutic suitability, inventory management or meal planning.

Revalidation decision: retain.

## Requirements

The requirements are coherent with the problem. The important semantic distinctions remain necessary:

- member targets versus aggregate household planning demand;
- desired/reference intake versus safety limits;
- known zero versus unknown/trace/limit-qualified nutrient evidence;
- theoretical food identity versus commercial SKU/offer;
- purchased quantity versus planned utilized quantity;
- nutrition derivation date versus market as-of instant;
- domain partial result versus technical execution failure.

Revalidation decision: retain these distinctions as mandatory downstream contracts.

## Strategic domain

The four-context model is retained. A three-context alternative that merges Food Knowledge with Market Catalog was rejected because normalized food truth changes independently from commercial product/offer truth and is consumed independently by Purchase Planning. Merging Nutrition Targeting into Purchase Planning was rejected because nutrition-standard applicability and target derivation have independent language, provenance and change cadence.

No additional Bounded Context is justified for solver, imports, reporting, persistence or CLI; these are realization responsibilities rather than separate semantic ownership.

## Tactical domain

The existing tactical concepts remain sufficient for the MVP. No new aggregate is introduced solely for persistence or solver convenience.

Purchase Planning owns decision policy and result semantics, but not authoritative copies of household, food or market state. Its planning input is a calculation snapshot, not durable business state.

## Quality attributes

Priority order for the first implementation:

1. semantic correctness and provenance preservation;
2. deterministic/reproducible planning for identical explicit inputs;
3. explainable result classification and diagnostics;
4. modular change isolation across the four semantic owners;
5. local operational simplicity;
6. performance sufficient for the accepted MVP dataset.

No availability, horizontal scaling or distributed deployment target justifies network decomposition.

## Security and privacy

The MVP is local/single-operator and has no remote authentication boundary. Nevertheless, member profile data is personal data and must remain local to the configured datastore/output path. Logs/diagnostics must not dump full profiles or complete nutrition snapshots by default. Imported external data is untrusted input and must be validated before becoming canonical provider state.

A future multi-user/network interface requires a new security/interface design; it is not silently covered by this MVP.

## Architecture

One modular monolith remains the smallest architecture preserving ownership. One relational datastore is acceptable provided table ownership is logical and cross-context access occurs only through provider application contracts.

The coherent-read requirement is architectural: one planning run must observe mutually coherent provider facts before optimization. The mechanism is not architectural; transaction/database technology is Implementation Design.

No internal HTTP, message bus, event sourcing, CQRS infrastructure, generic repository layer or service-per-context deployment is justified.

## Application

The primary application journey remains Generate Purchase Plan:

derive target → obtain canonical food/market facts → capture immutable planning input → optimize → independently calculate/report accepted result → optionally enrich positive mapped gaps with theoretical food suggestions.

The solver is a replaceable technical mechanism behind a Purchase Planning-owned contract. It does not own business ranking semantics or authoritative reporting.

## Data

Persistent ownership follows semantic ownership. Derived Member/Household targets and Planning Input Snapshot are rebuildable calculation products, not required durable state. Purchase Plan history is outside MVP.

Cross-context identifiers are opaque references, not relational ownership.

## Interface

A deterministic non-interactive CLI remains the minimum complete first interface because the product problem does not require remote access, authentication or interactive presentation. The interface exposes explicit household, derivation date and market-as-of; current time is never an implicit semantic input.

## Engineering policy

Clean inward dependencies, provider-owned cross-context contracts, consumer-shaped ports, KISS/YAGNI and explicit mapping boundaries are retained. SOLID is applied as observable obligations rather than class-count rules.

## Component design

Component design is retained but corrected to be technology-neutral. It fixes responsibilities and contracts, not Python Protocols, SQLAlchemy classes, SQLite connection mechanics or a SCIP wrapper representation.

## Verification

Verification is specified from accepted semantics rather than existing tests. Required evidence covers domain derivation, evidence-state preservation, market executability, planning ranking/outcomes, architecture boundaries, coherent capture, persistence round-trips, deterministic interface behavior and technical-failure separation.

## Material design questions

No P0/P1 question remains for the accepted first-MVP implementation boundary. Questions about remote UI/API, multi-user authorization, saved plan history, inventory, meals, individual allocation and automated source acquisition are future-scope questions and do not block this implementation.
