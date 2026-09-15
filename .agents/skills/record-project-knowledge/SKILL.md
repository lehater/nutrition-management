---
name: record-project-knowledge
description: "Use when a Nutrition Management discussion produced durable requirements, domain knowledge, architecture decisions, unresolved material questions or milestone knowledge that must be fixed in the repository rather than left in conversation history."
---

# Record Project Knowledge

Use `docs/process/document-lifecycle.md`.

## Procedure

1. Harvest only consequential content from the discussion/evidence.
2. Split mixed statements by semantic owner: requirement, domain, architecture, ADR rationale, execution state.
3. Preserve source evidence separately from interpretation when later reinterpretation may matter.
4. Mark non-accepted content explicitly as proposal/hypothesis/unknown/conflict.
5. Update the highest canonical owner first; link downward instead of duplicating paragraphs.
6. Use an ADR only when the rationale/trade-off/supersession needs durable history.
7. Use `docs/baseline/` only when an explicit milestone snapshot/provenance packet is useful; Git history is the normal archive.
8. Update `docs/plans/active/README.md` only for current resumable execution state.
9. Remove temporary notes once durable outcomes are absorbed.

Do not persist chat transcripts as project documentation.
