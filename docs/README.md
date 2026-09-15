# Nutrition Management documentation

The `docs/` tree is a versioned project knowledge base, not a dump of discussions.

## Ownership map

| Area | Question answered |
|---|---|
| `problem.md` | What problem/outcome is accepted, what evidence and scope assumptions frame the product? |
| `requirements/` | What observable behavior or quality must hold? |
| `domain/` | What does the domain mean, and who owns which semantic facts/decisions? |
| `architecture/` | How will accepted semantics be realized while preserving boundaries and constraints? |
| `decisions/` | Which consequential project choice was made, why, and what does it supersede? |
| `plans/active/` | What is being executed now, what is blocked, and what is next? |
| `baseline/` | Which explicit historical project snapshot/provenance packet is worth retaining? |

## Reading rule

Start from the task, not from the whole documentation tree. Read the nearest applicable project instructions and only the canonical owners required by the question.

## Writing rule

Accepted project truth goes into its owning living artifact. Durable rationale goes into an ADR when needed. Git history is the default archive.
