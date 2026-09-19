# Engineering Design Policy

Status: research candidate for Nutrition Management.

## Purpose

Constrain implementation-facing design so coding agents do not choose architectural discipline implicitly. This policy does not redefine product/domain behavior and does not require patterns without an accepted variation or boundary.

## Core policy

### Clean Architecture / dependency rule

- Source dependencies point inward: adapters/infrastructure → application → domain.
- Domain policy depends on no database, solver, transport, framework, composition or Harness API.
- Application use cases depend on domain policy and on ports/provider application contracts, not concrete infrastructure.
- Infrastructure implements application-owned ports or provider-owned persistence/application seams.
- Composition is the only layer allowed to select concrete implementations and coordinate infrastructure across context boundaries.
- Cross-context consumers use provider-owned application contracts; they never depend on another context's repository/table model.

### SOLID obligations

**SRP.** Every public component has one coherent responsibility and one principal reason to change. Orchestration, mapping, persistence, solver mechanics and domain calculation are separate responsibilities when they vary independently.

**OCP.** Introduce a stable seam only for variation already required by accepted design (solver, persistence/provider access, external adapter). Do not add plugin frameworks or abstract factories for hypothetical future variation.

**LSP.** Every implementation of a port must preserve the port's documented inputs, outputs, errors and semantic invariants. Tests may substitute fakes without changing use-case behavior.

**ISP.** A consumer-facing port exposes only operations required by that consumer. Do not create one repository/service interface spanning unrelated context capabilities.

**DIP.** High-level application policy owns or consumes abstractions; it does not import concrete infrastructure. Provider-owned cross-context contracts are treated as semantic abstractions and remain owned by the provider.

### General design constraints

- KISS: choose the smallest component set that makes accepted responsibilities and dependency direction explicit.
- YAGNI: no extension point, base class, generic repository or event bus without an accepted current need.
- SoC: parsing/transport, orchestration, domain policy, persistence mapping and solver mechanics remain separable.
- CQS: query/read contracts do not mutate provider state; state-changing import/command operations are explicit.
- LoD / Tell Don't Ask: use-case code collaborates through direct contracts and domain behavior; it does not navigate repository/entity internals to implement another owner's policy.
- Composition over inheritance: prefer composition/ports; inheritance requires an actual substitutability relationship.
- DbC: public ports state required preconditions, returned guarantees and domain-vs-technical failure semantics where they matter.
- Fail Fast: invalid technical inputs and impossible invariant states fail at the owning boundary; they are not silently converted to domain outcomes.
- POLA: API/component behavior follows the accepted domain vocabulary and avoids hidden time/default/global state.

## Component acceptance obligations

A Component Design artifact is acceptable only when it:

1. lists public implementation components by bounded context/layer;
2. assigns one coherent responsibility to each;
3. identifies ports/contracts and which side owns each abstraction;
4. shows dependency direction for every cross-layer/cross-context collaboration;
5. identifies representation mapping boundaries;
6. identifies the composition root and construction relationships;
7. traces the Generate Purchase Plan use case through collaborating components;
8. explicitly lists forbidden dependencies;
9. distinguishes required seams from implementation freedoms;
10. contains no abstraction justified only by possible future requirements.

## Explicit non-rules

The following are not required for the current MVP merely because they are common patterns:

- CQRS split infrastructure;
- event sourcing;
- domain event bus;
- mediator framework;
- generic repository;
- unit-of-work abstraction beyond the accepted coherent-read composition boundary;
- REST/HATEOAS;
- service-per-bounded-context;
- dependency-injection framework.

They may be introduced only after an accepted requirement/design decision creates the need.
