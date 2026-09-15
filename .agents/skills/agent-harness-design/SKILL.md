---
name: agent-harness-design
description: "Use when designing or reviewing the Nutrition Management repository harness: AGENTS routing, Skills, project-knowledge ownership, document lifecycle, change lifecycle, active execution state and deterministic validators. Prefer the smallest change that removes a demonstrated harness problem."
---

# Agent Harness Design

Audit:
- source-of-truth ownership;
- no-invention and unknown handling;
- Strategic/Tactical DDD routing;
- document acceptance/supersession/fixation;
- progressive context loading;
- current-task recoverability;
- Skill overlap;
- deterministic validation opportunities;
- stale/duplicated truth;
- unnecessary process complexity.

Rules:
- one agent plus repository instructions/Skills is the default;
- protocols own reusable process semantics; Skills explain how to execute judgement-heavy work;
- deterministic invariants belong in validators when practical;
- current project facts never belong in reusable Skill bodies;
- do not turn the conceptual lifecycle into a runtime workflow engine without demonstrated need;
- run `make harness-check` after harness changes.
