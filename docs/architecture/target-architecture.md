# MVP Target Architecture

Status: `proposed` while S3 review is in progress.
Lifecycle layer: `S3 Architecture`.

## Purpose

Define the smallest realization structure that preserves the accepted S1/S2 contracts without introducing implementation-only choices prematurely.

This architecture realizes, but does not redefine, the accepted Bounded Contexts and ADR-002 through ADR-007.

## System topology

The MVP is one deployable modular-monolith application process backed by one transactional relational database.

Inside the process, four context-aligned modules preserve semantic ownership:

```text
presentation/import adapters
          |
          v
+--------------------------- application process ---------------------------+
|                                                                           |
|  Nutrition Targeting   Food Knowledge   Market Catalog   Purchase Planning|
|  -------------------   --------------   --------------   -----------------|
|  application           application      application      application       |
|      |                     |                |                |              |
|  domain                domain            domain            domain          |
|      ^                     ^                ^                ^              |
|  persistence/import    persistence      persistence       solver/result    |
|  adapters              adapters         adapters          adapters         |
|                                                                           |
+---------------------------------------------------------------------------+
                              |
                              v
                    one relational database
             (context-owned logical persistence)
```

No Bounded Context is a network service in the MVP.

## Module boundaries

### Nutrition Targeting

Owns application use cases and persistence for:

- Household/Household Member current profile state;
- active/versioned Nutrition Standard Sets and their reference/formula data;
- derivation of Member Nutrition Targets and Household Nutrition Target;
- target-to-Food-Knowledge mapping provenance accepted by ADR-004.

Publishes planning-facing contracts that return the derived Household Nutrition Target plus the provenance required by the Context Map.

### Food Knowledge

Owns application use cases and persistence for:

- Base Foods;
- canonical BLS-based nutrient components and derived Nutrient Measures;
- source/provenance data;
- Food Categories and category membership.

Publishes planning/catalog-facing canonical food facts. It never exposes persistence entities as a cross-context contract.

### Market Catalog

Owns application use cases and persistence for:

- Product Cards/SKUs;
- normalized nutrient overrides;
- edible package-quantity conversions;
- Merchants;
- Fulfilment Channels;
- Offers and temporal/commercial observations.

It consumes Food Knowledge through the published food contract when building/validating effective SKU nutrient facts. It does not write Food Knowledge tables.

Publishes an executable-market projection for an `as_of` planning time.

### Purchase Planning

Owns:

- planning-run orchestration;
- immutable Planning Input Snapshot capture;
- solver model construction;
- accepted ADR-007 ranking/tie-breaking semantics;
- solver adapter boundary;
- post-solver invariant validation and reporting calculation;
- persisted Purchase Plan/result and calculation evidence.

Purchase Planning does not own authoritative member, food or market facts copied into a snapshot.

## Internal dependency rules

Within a context:

```text
infrastructure/adapters -> application -> domain
```

Allowed cross-context dependency direction follows the accepted Context Map:

```text
Nutrition Targeting -----> Purchase Planning
Food Knowledge ----------> Market Catalog
Food Knowledge ----------> Purchase Planning
Market Catalog ----------> Purchase Planning
```

The arrows mean provider contract -> consumer use; they do not permit consumer access to provider domain internals or tables.

A context may expose stable contract DTO/value structures at its application boundary. Those contracts carry provider terminology and identifiers required by the Context Map but are not shared mutable domain entities.

## Persistence and ownership

One physical relational database is used for MVP simplicity.

Architecture constraints:

- every table/collection has exactly one owning context;
- only the owning context's persistence adapter writes its tables;
- consumers do not read provider tables directly;
- no cross-context ORM relationships or shared persistence entities;
- foreign identifiers crossing a context boundary are stored as scalar identifiers/provenance, not as shared entity ownership;
- schema migrations preserve context ownership even when deployed together;
- database-vendor-specific features must not leak into domain policy.

The concrete database product and migration framework are S4 choices.

## Primary planning flow

The Generate Purchase Plan application flow is:

1. accept a household/planning request and establish one planning `as_of` / derivation date;
2. inside one consistent-read boundary, request the planning contracts from Nutrition Targeting, Food Knowledge and Market Catalog;
3. assemble an immutable Planning Input Snapshot with provider identifiers, versions and observation provenance;
4. end the database read boundary;
5. transform the snapshot into the solver problem while preserving ADR-007 semantics;
6. invoke the in-process Optimization Solver adapter;
7. revalidate material executable invariants and calculate reportable nutrition/variety/cost facts from the returned quantities;
8. persist the Purchase Plan together with sufficient immutable calculation evidence/provenance;
9. return one primary plan, or the accepted `partial` / `no_executable_plan` domain outcome.

A technical solver/import/database failure is not represented as `partial` or `no_executable_plan`; technical failure remains a separate application error.

## Planning snapshot contract

The Planning Input Snapshot is immutable after assembly and is private to Purchase Planning execution/persistence.

It records the exact calculation evidence necessary to prevent later upstream edits from changing the meaning of an already produced plan. At minimum it identifies:

- calculation date/horizon;
- standards/policy version;
- resolved household target and target mappings;
- food/component/measure/category facts used by candidate SKUs and suggestions;
- effective SKU nutrient facts and edible package quantities;
- executable offers/channels with price/currency/availability/observation/validity/order conditions.

Snapshot copies are evidence, not new authoritative provider state.

## Optimization integration

The solver is an infrastructure dependency behind a Purchase Planning-owned port.

Architecture requirements for the S4 solver choice:

- callable in-process;
- supports integer and continuous decisions plus conditional/binary constraints required by the accepted planning model;
- can preserve ADR-007 lexicographic/sequential objective order without hidden weighted compromises;
- exposes infeasible/optimal/technical-error states distinctly;
- supports deterministic execution or a fixed recorded seed;
- does not become the source of reportable business calculations.

Purchase Planning owns model construction and output interpretation. Domain/report calculations are performed from the returned decision quantities using project policy.

## Data import architecture

MVP data acquisition is manual/import based.

Import adapters are outer infrastructure. They:

1. parse external source representation;
2. translate it into the owning context's application commands/import records;
3. invoke context validation/normalization;
4. persist only through the context's persistence adapter.

Imports never bypass canonical nutrient, edible-quantity, offer validity or provenance rules through direct database writes.

Automatic external synchronization, scraping schedules and message-driven ingestion are outside the MVP architecture.

## Temporal and version semantics

Architecture preserves accepted time/version facts rather than replacing them with implicit current-state reads:

- target derivation uses an explicit derivation date and immutable standard-set version;
- Offer/Fulfilment observations preserve `observed_at` and explicit validity bounds;
- planning uses one `as_of` snapshot point;
- an already persisted plan remains attached to the evidence used at calculation time;
- later standards/catalog/price changes do not mutate historical planning evidence.

## Error boundaries

Application errors distinguish at least:

- invalid/inapplicable source input before planning;
- unavailable/unsupported data that is an accepted domain diagnostic;
- `no_executable_plan` as an accepted Purchase Planning outcome;
- persistence/import/solver technical failures.

Infrastructure failures must not be converted into domain outcomes that imply a valid optimization result.

## Explicit non-decisions for S4

The following are intentionally not fixed by S3 because no accepted upstream requirement depends on them:

- programming language/runtime;
- application/web framework;
- relational database vendor;
- ORM/query library;
- dependency-injection framework;
- HTTP/CLI/UI presentation technology;
- concrete optimization library;
- deployment hosting provider.

S4 may choose these only within the architecture constraints above.

## S3 invariants

- no Bounded Context is split into an independently deployed service without reopening S3;
- no consumer directly reads/writes another context's persistence model;
- domain policy depends on no framework, persistence or solver API;
- one planning solve operates only on one immutable Planning Input Snapshot;
- provider reads do not occur during the optimization phase after snapshot assembly;
- persisted plan evidence does not become authoritative provider state;
- solver configuration cannot change ADR-007 business ordering through hidden weights/tolerances;
- technical execution failures remain distinct from accepted domain outcomes.

## S3 review questions

Before marking S3 `PASS`, verify:

1. whether one physical relational store is sufficient for every accepted consistency/provenance requirement;
2. whether the Planning Input Snapshot carries enough evidence for plan explanation without becoming duplicate authoritative state;
3. whether the solver port is narrow enough to remain replaceable while preserving deterministic ADR-007 policy;
4. whether any proposed cross-context dependency bypasses the accepted Context Map;
5. whether any runtime/asynchronous component is being introduced without requirement evidence.
