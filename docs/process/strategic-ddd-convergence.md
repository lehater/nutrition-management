# Strategic DDD convergence

## Purpose

Converge on coherent semantic ownership and Bounded Context boundaries when S2 work shows that ownership, language or relationships are unsettled.

The current model is a hypothesis to challenge, not proof that existing boundaries are correct.

## Inputs

Load only the affected scope:
- accepted requirements creating the semantic need;
- affected domain/context artifacts;
- accepted ADRs constraining ownership;
- concrete consumer/provider semantic needs;
- code/persistence only as secondary evidence when needed.

## Boundary evidence

Capabilities, journeys and use cases are evidence, not automatic Bounded Contexts.

Look for semantic cohesion around:
- ubiquitous language;
- authoritative decisions/facts;
- identity, lifecycle and invariants;
- authority/responsibility;
- independent change;
- stable semantic inputs/outputs.

For each candidate context make explicit:
- purpose;
- authoritative responsibility;
- decisions/facts it owns;
- key identities/lifecycles/invariants;
- required inputs;
- public outputs/semantic facts.

## Bad-boundary signals

- two contexts claim authority over the same fact/decision;
- no context owns a required fact/decision;
- one context must understand peer-private entities/state transitions;
- one semantic lifecycle/invariant is artificially split;
- the boundary exists only because of a table, service, screen, package or deployment.

## Relationship contract

For each material context edge state:
- provider/semantic owner;
- consumer;
- semantic input/request when applicable;
- semantic output/fact;
- identity references crossing the boundary;
- time/unknown/provenance semantics where material;
- consumer obligations and forbidden reinterpretation.

The contract is semantic before it is HTTP, messaging, Python/Java/TypeScript or storage design.

## Convergence

Strategic work is coherent for the affected scope when:
- authoritative responsibilities have one owner;
- required relationships and semantic contracts are explicit;
- consumers do not need peer-private domain models;
- no unresolved P0/P1 ownership/boundary contradiction remains;
- remaining technical delivery questions can safely be routed to Architecture.

Promote only accepted results to `docs/domain/`. Do not retain permanent discovery/capability-clustering reports by default after their useful conclusions have been absorbed.
