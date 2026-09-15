---
name: domain-model-change
description: "Use when a requirement, design question, code finding or stakeholder clarification may change Nutrition Management domain semantics: ubiquitous language, semantic identity/lifecycle, invariants, responsibility/authority ownership, Bounded Context boundaries or cross-context contracts."
---

# Domain Model Change

Use `docs/process/domain-change-protocol.md` to classify the highest affected layer.

## Procedure

1. State the trigger as evidence, not as a conclusion.
2. Classify the highest affected owner: Requirements, Tactical DDD, Strategic DDD, Architecture or implementation-only.
3. Read only the smallest affected canonical evidence.
4. Separate accepted facts, constraints, proposals, hypotheses, unknowns and conflicts using `docs/process/decision-protocol.md`.
5. If Strategic DDD is affected, use `docs/process/strategic-ddd-convergence.md`.
6. If Tactical DDD is affected inside an accepted context, use `docs/process/tactical-ddd-stage.md`.
7. Update the highest affected canonical owner first.
8. Propagate only the required downstream delta.

## Guardrail

A journey, use case, capability, class, table, API, package, service or deployment unit is not automatically a Bounded Context.
