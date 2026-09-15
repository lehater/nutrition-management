# ADR-008 — MVP uses a modular monolith with context-owned persistence

Status: `accepted` for the S3 baseline.

Date: 2026-09-15.

## Context

S2 accepts four Bounded Contexts: Nutrition Targeting, Food Knowledge, Market Catalog and Purchase Planning. These are semantic ownership boundaries, not deployment units. The product requirements do not require independent scaling, independent deployment, cross-team ownership, external public APIs, asynchronous integration or fault isolation between those contexts.

The repository guardrails require the smallest architecture that preserves accepted semantics and explicitly discourage distributed services and shared business-model packages without demonstrated need.

At the same time, a single undifferentiated application/data model would make it easy for Purchase Planning or Market Catalog to bypass provider-owned semantics through direct table access or shared entities.

## Decision

### Deployment topology

The MVP is one deployable application process: a **modular monolith**.

The process contains four context-aligned modules:

- `nutrition-targeting`;
- `food-knowledge`;
- `market-catalog`;
- `purchase-planning`.

A Bounded Context maps to one logical application/domain module in the MVP, not to a network service.

No internal message broker, service mesh, distributed transaction, RPC boundary or independently deployed worker is introduced for the initial architecture.

### Module structure and dependency direction

Each context module has an inward dependency direction:

`adapters/infrastructure -> application -> domain`

The domain layer contains domain policy and accepted semantics and must not depend on persistence, transport, framework or dependency-injection APIs.

Application code owns use-case orchestration and module-facing interfaces. Infrastructure adapters implement persistence/import/solver/transport seams.

Cross-context collaboration occurs only through explicit provider-owned application contracts derived from the accepted Context Map. A consumer may depend on a provider's published contract, but not on its domain internals or persistence representation.

There is no project-wide shared business-domain model. Shared code is limited to semantically neutral technical primitives when duplication would otherwise create concrete implementation risk.

### Persistence topology

The MVP uses one transactional **relational database** as the physical persistence store.

The database technology/vendor is intentionally deferred to S4 because no accepted requirement currently depends on vendor-specific behavior.

Each context owns its logical persistence namespace/tables and mapping. Direct cross-context writes are forbidden. Cross-context reads that bypass published application contracts are also forbidden, including ad-hoc joins that reinterpret provider-owned state in the consumer.

One physical database is a deployment simplification, not shared semantic ownership.

### Transaction boundaries

Ordinary state-changing transactions are owned by one context module.

No use case requires a distributed transaction between contexts in the MVP. Cross-context planning is handled by immutable planning input capture as defined by ADR-009 rather than by holding a write transaction across the whole optimization run.

### External adapters

Manual/import data acquisition is implemented through adapters that call the owning context's application use cases. Imports must not write directly to persistence tables.

The external interaction transport (for example HTTP, CLI or another presentation adapter) is not fixed by S3 because accepted requirements do not constrain it. The architecture requires only that transport remain an outer adapter over application use cases.

## Consequences

- semantic context boundaries remain visible without paying distributed-systems cost;
- one process permits ordinary in-memory calls across explicit module contracts;
- one relational store provides simple transactions and referential persistence while table ownership remains context-local;
- direct SQL joins across context-owned persistence are not a supported integration mechanism;
- a future split into services remains possible at published contracts, but is not designed prematurely;
- database vendor, web framework and presentation technology can be selected in S4 without changing accepted semantic ownership.

## Alternatives considered

### One service/database per Bounded Context

Rejected for MVP. There is no accepted requirement for independent deployment/scaling/fault isolation, and the additional network, consistency and operational complexity would not create product value at this stage.

### One layered application with one shared domain/data model

Rejected because it would erase the accepted ownership boundaries and make provider semantics bypassable through shared entities and tables.

### Separate physical database per context inside one process

Rejected initially because it increases migration/transaction/operational complexity without an accepted isolation requirement. Logical ownership inside one database is sufficient for the MVP.

### Document-oriented or graph persistence as the primary store

Rejected as the baseline because the accepted model is dominated by structured relationships, versioned reference data, catalog relations, offers/order conditions and auditable planning provenance. No accepted requirement needs graph/document-store-specific behavior.

## Supersession

Supersedes: none.
Superseded by: none.
