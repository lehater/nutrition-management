# Documentation scope

Apply root `AGENTS.md` first.

## Canonical ownership

- `domain/` — Strategic/Tactical DDD: what concepts mean and who owns them.
- `requirements/` — what externally meaningful behavior/quality must hold.
- `architecture/` — how semantic owners compose and which structural/runtime constraints preserve correctness.
- `decisions/` — consequential decisions and explicit supersession.
- `plans/active/` — what work is current, blocked and next.
- `baseline/` — explicit accepted snapshots/provenance, not living truth.
- `process/` — reusable repository protocols.

Keep each decision at its highest owning layer and link downward instead of retelling it.

## Document discipline

Use `process/document-lifecycle.md` for acceptance, fixation, supersession and snapshots.

A file path does not make a statement true. Classify the statement by meaning and acceptance status.

Historical milestone packets must not remain in living `requirements/`, `domain/` or `architecture/` merely as archives. Absorb durable outcomes into current owners; use ADR/baseline/Git history for history.

Completed temporary planning/discovery notes are removed once accepted knowledge and unresolved durable problems have been promoted.
