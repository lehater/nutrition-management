# Nutrition Management documentation

The `docs/` tree is a versioned project knowledge base, not a dump of discussions.

## Ownership map

| Area | Question answered |
|---|---|
| `requirements/` | What observable behavior or quality must hold? |
| `domain/` | What does the domain mean, and who owns which semantic facts/decisions? |
| `architecture/` | How will accepted semantics be realized while preserving boundaries and constraints? |
| `decisions/` | Which consequential choice was made, why, and what does it supersede? |
| `plans/active/` | What is being executed now, what is blocked, and what is next? |
| `baseline/` | Which explicit historical snapshot/provenance packet is worth retaining? |
| `process/` | How do we perform recurring project work? |

## Reading rule

Start from the task, not from the whole documentation tree. Read the nearest `AGENTS.md`, the smallest applicable Skill and only the canonical owners required by the question.

## Writing rule

Accepted truth goes into its owning living artifact. Durable rationale goes into an ADR when needed. Git history is the default archive. See `process/document-lifecycle.md`.
