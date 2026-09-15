# Change lifecycle

## Purpose

Route non-trivial changes from evidence to implementation without allowing a lower layer to invent unresolved higher-layer truth.

```text
S0 Problem / Evidence
  -> S1 Requirements
  -> S2 Domain Design
  -> S3 Architecture
  -> S4 Implementation Readiness
  -> Implementation
```

This is a reasoning model, not a required runtime workflow engine and not a waterfall. Enter at the earliest layer whose accepted truth may change.

## Stage contract

Each stage has:

```text
Inputs -> Work -> Outputs -> Gate
```

A document existing does not mean the gate passed.

### S0 Problem / Evidence

Input: raw need, observation, contradiction or opportunity.
Output: bounded problem/outcome, relevant evidence, explicit unknowns.
Gate: the problem is understood well enough to state requirements without inventing intent.

### S1 Requirements

Input: accepted problem/evidence.
Output: observable behavior, constraints and quality expectations.
Gate: downstream domain work can rely on the required behavior.

### S2 Domain Design

Input: accepted requirements plus affected domain truth.
Output: coherent semantic ownership, language, identities, lifecycles, invariants and context contracts.
Gate: architecture does not need to guess domain meaning.

Strategic and Tactical DDD are routes inside S2, not separate top-level stages.

### S3 Architecture

Input: accepted requirements/domain guarantees.
Output: realization structure and technical constraints that preserve them.
Gate: implementation planning does not need to invent architectural ownership or consistency rules.

### S4 Implementation Readiness

Input: accepted architecture plus current code/operational state.
Output: bounded implementation slice, tests/migrations/risks and executable acceptance evidence.
Gate: the slice is safe to implement without unresolved upstream P0/P1 questions.

## Routing

- implementation-only detail -> S4;
- architecture concern -> S3;
- domain semantic concern -> S2;
- accepted behavior/quality concern -> S1;
- unclear need/conflicting evidence -> S0.

When uncertain, route earlier rather than silently deciding downstream.

## Outcomes

- `PASS` — current layer is sufficient for the next dependent layer.
- `REWORK` — deficiency belongs to the current layer; fix the smallest delta.
- `REOPEN(Sx)` — a missing/changed guarantee belongs to an earlier layer; return there and revalidate affected downstream work.
- `BLOCKED` — required knowledge/owner decision is unavailable; record the unknown and stop the affected path.

P0/P1 findings prevent PASS for guarantees they affect. P2/P3 may remain when non-blocking.

## No-progress rule

Repeat work only when the iteration is expected to change evidence, accepted knowledge, decision state, problem state or the scope of uncertainty. Repeating the same reasoning is blockage, not progress.
