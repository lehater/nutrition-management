# Data Design

Status: accepted for MVP implementation readiness.

## Responsibility

Define the relational persistence representation required by accepted domain, application and architecture contracts. Persistence represents provider-owned state; it does not create cross-context semantic ownership.

## Store and ownership

The accepted architecture uses one relational store for the modular monolith. Data Design owns logical persistence representation, integrity and consistency semantics; the concrete database engine, driver, journal/durability settings and migration tooling are Implementation Design decisions.

Logical ownership remains explicit:

- `nt_`: Nutrition Targeting;
- `fk_`: Food Knowledge;
- `mc_`: Market Catalog;
- `pp_`: Purchase Planning only if future accepted durable planning-owned state requires it.

There are no cross-context foreign keys. Cross-context references are opaque provider identifiers.

## Nutrition Targeting representation

Persist:

- current member profile keyed by `member_id`, associated with `household_id`;
- date of birth, sex, height, current weight/date, PAL and optional target weight/date;
- versioned Nutrition Standard Sets;
- nutrient target/reference records;
- member safety-reference records.

The active standard is data, not code. Derived household targets are computed application results and are not authoritative persisted aggregates.

## Food Knowledge representation

Persist:

- Base Food identity, name, category and source provenance;
- nutrient facts keyed by Base Food + canonical measure;
- explicit evidence status;
- amount only where the evidence state permits a quantitative value.

BLS/source-specific ingestion must normalize into this owned representation without erasing raw/source provenance required by accepted Food Knowledge decisions.

## Market Catalog representation

Persist:

- Product Card/SKU with opaque Base Food identifier and edible grams per package;
- normalized SKU nutrient overrides;
- Fulfilment Channel with merchant, mode, currency, order conditions and temporal provenance;
- Offer with SKU/channel identifiers, price/currency, availability, observation and validity bounds.

Offer executability is derived from accepted Market Catalog semantics; persistence does not encode an alternative business policy.

## Purchase Planning representation

The MVP does not require durable Purchase Plan history or durable Planning Input Snapshots.

A Planning Input Snapshot is immutable in-memory calculation input for one execution. It is discarded after the run. Introducing saved plans, replay snapshots or planning tables requires an accepted upstream requirement.

## Scalar encoding

Authoritative decimal quantities and money require an exact persistence representation that round-trips accepted decimal semantics without binary floating-point becoming authoritative. The concrete relational encoding is an Implementation Design choice.

Dates and instants require unambiguous persistence representations preserving accepted date/time semantics; instants remain normalized to UTC at the persistence boundary. Currency is an explicit code beside amount.

Solver floating-point coefficients exist only at the solver adapter boundary. Reportable values are recalculated from domain/application values.

## Consistent planning read

Snapshot assembly uses one explicit coherent relational read scope spanning all provider reads. Provider repositories participate in that scope without exposing the concrete database transaction/connection through domain/application contracts.

The read scope closes before solver execution. The concrete database isolation/snapshot mechanism must realize this semantic contract and is selected by Implementation Design.

## Migrations

The modular monolith has one ordered schema-evolution stream, while every table/change retains one context owner. The concrete migration tool is selected by Implementation Design.

Migration rules:

- forward schema changes preserve accepted provider semantics;
- no migration introduces cross-context relational ownership;
- source/reference data migrations remain distinguishable from schema migrations where practical;
- verification exercises migrations against the selected concrete relational implementation rather than only an in-memory substitute when that would bypass accepted transaction/durability semantics.

## Integrity boundary

Database constraints enforce representation-level integrity within a context. Domain/application validation remains authoritative for semantic invariants that cannot be represented safely as relational constraints.

A schema change that changes domain meaning, context ownership or planning consistency semantics must reopen the corresponding upstream design rather than being treated as a local migration detail.

## Data classification contract

Persistent data is classified for engineering handling before implementation:

- member/household profile and nutrition/safety-reference data are personal domain data and must not be copied into diagnostics, fixtures or exports by default;
- Food Knowledge source facts and provenance are externally sourced reference data whose source identity and normalization evidence must remain traceable;
- Market Catalog observations are commercial/temporal domain data and retain observation/validity provenance;
- implementation metadata such as migration revision identifiers is operational data and carries no domain authority.

Classification does not itself decide legal/privacy obligations. If a classification triggers such an obligation, that decision is routed to the owning governance/obligation authority.

## Data lifecycle contract

Lifecycle is explicit per data class:

- current member/profile state is mutable provider-owned state; updates replace current state while preserving only history required by an accepted requirement;
- Nutrition Standard Sets and other versioned reference sets are immutable-by-version once accepted for use;
- imported Food Knowledge/Market data is normalized into canonical provider state while retaining required source/provenance identity;
- schema evolution is performed through the single accepted migration stream and must preserve context ownership and representation invariants;
- Planning Input Snapshots and returned Purchase Plans remain non-durable for the MVP and are discarded after the execution/result lifecycle;
- deletion, archival or long-term retention beyond these rules requires an explicit upstream product/governance decision rather than an implementation default.
