# Documentation scope

Apply root `AGENTS.md` first.

## Canonical ownership

- `domain/` — Strategic/Tactical DDD: what concepts mean and who owns them.
- `requirements/` — what externally meaningful behavior/quality must hold.
- `architecture/` — how accepted semantics are realized and which structural/runtime constraints preserve correctness.
- `decisions/` — consequential project decisions and explicit supersession.
- `plans/active/` — what work is current, blocked and next.
- `baseline/` — explicit accepted snapshots/provenance, not living truth.

Keep each project decision at its highest owning layer and link downward instead of retelling it.

Historical milestone packets must not remain in living `requirements/`, `domain/` or `architecture/` merely as archives. Absorb durable outcomes into current owners; use ADR/baseline/Git history for history.

Completed temporary planning/discovery notes are removed once accepted knowledge and unresolved durable project problems have been promoted.
