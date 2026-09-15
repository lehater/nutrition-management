# Decision and unknown protocol

Every consequential statement used for design is classified along two independent axes.

## Axis 1 — semantic owner

- **S0 Problem / Evidence** — need, observation, desired outcome, problem boundary.
- **S1 Requirement** — externally meaningful behavior, constraint or quality expectation.
- **S2 Domain Semantics** — meaning, identity, lifecycle, invariant and semantic ownership.
- **S3 Architecture** — realization structure and technical contracts/constraints.
- **S4 Implementation** — concrete executable detail not already constrained upstream.

Do not promote a concrete implementation choice into a product requirement merely because it is easy to test or was proposed confidently.

## Axis 2 — status

- **accepted/known** — supported by canonical truth or explicit owner decision at the correct layer;
- **constraint** — mandatory limitation downstream work must satisfy;
- **proposal** — candidate To-Be choice, not accepted;
- **hypothesis** — belief to validate;
- **unknown** — insufficient evidence/decision;
- **conflict** — authoritative sources disagree.

## Stakeholder evidence

Stakeholder statements, examples, goals, workarounds and risks are source evidence. They are not automatically requirements or domain truth.

When consequential evidence must survive a conversation, preserve a compact observation with enough provenance to reinterpret it later. Keep interpretation separate from the observation. Do not persist full chat transcripts.

## Classification questions

For a consequential statement ask:

1. What was actually observed or stated?
2. What semantic question does it answer?
3. What is its status: accepted, constraint, proposal, hypothesis, unknown or conflict?
4. Who can accept it?
5. What higher-level need/constraint is independent of the proposed realization?

## No-invention rule

Never represent a proposal, hypothesis or unknown as accepted truth because it makes implementation convenient.

For a material unknown:
1. inspect canonical repository evidence;
2. identify the owning layer;
3. resolve with evidence, a focused owner decision or explicit non-blocking deferral;
4. keep the affected gate closed while the unknown is blocking.

## Recording decisions

Put the accepted result in the smallest canonical owner. Create an ADR when the choice is consequential and its alternatives/rationale/supersession need durable history.

Chat transcripts are never canonical decisions.
