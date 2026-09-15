# Harness provenance

Status: `accepted`.

Date: 2026-09-15.

The initial Nutrition Management repository harness was adapted from the repository-local harness used in `lehater/napms`.

Adapted concepts:
- repository-local `AGENTS.md` routing;
- small reusable Skills;
- source-of-truth separation between requirements, domain, architecture, ADRs, plans, process and baseline;
- staged `S0 -> S4` change routing with upstream re-entry;
- Strategic/Tactical DDD separation;
- no-invention classification for evidence/proposals/unknowns/conflicts;
- repository fixation of durable knowledge instead of chat-history dependence;
- Git/ADR/baseline separation for current truth versus history.

Intentionally not copied as bootstrap truth:
- NAPMS product/domain concepts and Bounded Contexts;
- NAPMS-specific lifecycle state, gates and implementation authorization;
- backend/web technology choices;
- mature CI/evaluation machinery whose value has not yet been demonstrated for this repository.

Nutrition Management adds an explicit `docs/process/document-lifecycle.md` because formation, acceptance, fixation and supersession of project knowledge are a primary concern at bootstrap.
