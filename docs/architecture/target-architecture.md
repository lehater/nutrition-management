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
|  persistence/import    persistence      persistence       solver adapter   |
|  adapters              adapters         adapters                           |
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

Publishes planning/catalog-facing canonical food facts and theoretical gap-suggestion queries. It never exposes persistence entities as a cross-context contract.

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
- ephemeral immutable Planning Input Snapshot capture;
- solver model construction;
- accepted ADR-007 ranking/tie-breaking semantics;
- solver adapter boundary;
- post-solver invariant validation and reporting calculation;
- returned Purchase Plan composition and diagnostics.

Purchase Planning does not own authoritative member, food or market facts copied into a snapshot.

The MVP does not require saved Purchase Plan history or persistence of the complete Planning Input Snapshot.

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

## Consistent-read coordination

Planning snapshot assembly requires one coherent relational-database read snapshot across provider modules.

A neutral infrastructure-level read-snapshot coordinator at the application composition boundary opens/closes that consistent read scope. Provider application contracts remain persistence-agnostic; their persistence adapters participate in the scope without transaction/session/database objects appearing in domain or cross-context APIs.

This coordination is technical consistency infrastructure, not a new semantic owner.

## Primary planning flow

The Generate Purchase Plan application flow is:

1. accept a household/planning request and establish one planning `as_of` / derivation date;
2. enter one infrastructure-managed consistent-read scope;
3. request the optimization-facing contracts from Nutrition Targeting, Food Knowledge and Market Catalog;
4. assemble an immutable Planning Input Snapshot with provider identifiers, versions and observation provenance;
5. end the database read scope;
6. transform the snapshot into the solver problem while preserving ADR-007 semantics;
7. invoke the in-process Optimization Solver adapter;
8. revalidate material executable invariants and calculate reportable nutrition/variety/cost facts from the returned quantities;
9. when positive mapped gaps remain, query Food Knowledge for theoretical suggestions and retain suggestion-source provenance;
10. return one primary Purchase Plan, or the accepted `partial` / `no_executable_plan` domain outcome.

A technical solver/import/database failure is not represented as `partial` or `no_executable_plan`; technical failure remains a separate application error.

## Planning snapshot contract

The Planning Input Snapshot is immutable after assembly and private to one Purchase Planning execution.

It contains the exact facts needed for executable basket optimization at that run's `as_of` point, including:

- calculation date/horizon;
- standards/policy version;
- resolved household target and target mappings;
- food/component/measure/category facts required by executable candidate SKUs;
- effective SKU nutrient facts and edible package quantities;
- executable offers/channels with price/currency/availability/observation/validity/order conditions.

The snapshot is released after the run. It is not authoritative provider state and is not required to be stored.

Theoretical gap suggestions are intentionally fetched after the executable optimization result is known. They do not alter executable basket selection or outcome classification and carry their own Food Knowledge provenance in the returned result.

## Returned-plan provenance

The returned Purchase Plan carries the provenance required to interpret the recommendation at calculation time, including:

- derivation/calculation date and standards/policy version;
- selected Base Food/SKU/Offer/Fulfilment identifiers;
- selected price/condition observation and validity provenance;
- mapped coverage plus unsupported/indeterminate dimensions;
- suggestion-source provenance where theoretical alternatives are shown.

Exact historical replay of every candidate considered by an old run is not an MVP guarantee. Adding saved plan history or audit replay is future product behavior and must reopen the appropriate upstream lifecycle layer.

## Optimization integration

The solver is an infrastructure dependency behind a Purchase Planning-owned port.

Architecture requirements for the S4 solver choice:

- callable in-process;
- supports integer and continuous decisions plus conditional/binary constraints required by the accepted planning model;
- can preserve ADR-007 lexicographic/sequential objective order without hidden weighted compromises;
- exposes infeasible/optimal/technical-error states distinctly;
- supports deterministic execution or a fixed execution seed;
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
- executable optimization uses one `as_of` snapshot point;
- post-plan theoretical suggestions carry their own Food Knowledge provenance;
- later standards/catalog/price changes do not retroactively change the already returned plan meaning/provenance, even though the MVP does not guarantee exact replay.

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
- one executable-basket optimization operates only on one immutable Planning Input Snapshot;
- provider reads do not occur during the optimization phase after snapshot assembly;
- database transaction/session objects do not cross domain or context application-contract boundaries;
- full planning snapshots and plan history are not introduced as durable product state without an upstream requirement;
- solver configuration cannot change ADR-007 business ordering through hidden weights/tolerances;
- technical execution failures remain distinct from accepted domain outcomes.

## S3 review questions

Before marking S3 `PASS`, verify:

1. whether one physical relational store is sufficient for every accepted consistency/provenance requirement;
2. whether the ephemeral Planning Input Snapshot is the minimum consistency mechanism rather than duplicate authoritative state;
3. whether the solver port is narrow enough to remain replaceable while preserving deterministic ADR-007 policy;
4. whether any proposed cross-context dependency bypasses the accepted Context Map;
5. whether the neutral read-snapshot coordination leaks persistence concerns into provider/domain contracts;
6. whether any runtime/asynchronous component is being introduced without requirement evidence.
