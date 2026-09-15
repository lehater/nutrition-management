# Working loop

## Persistence model

```text
conversation = disposable execution context
canonical docs = durable accepted knowledge
active plan = compact resumable execution state
working branch = durable WIP/checkpoints
main = curated integrated history
```

## Checkpoint

Checkpoint when a coherent increment is complete, a stage/owner changes, the next task depends on the state, or losing work would be costly.

Before discarding conversation context:
1. promote accepted requirements/domain/architecture truth into canonical owners;
2. preserve consequential source evidence separately from interpretation when needed;
3. record material unresolved blockers/unknowns in the smallest current owner;
4. update `docs/plans/active/README.md` if current work must be resumed later;
5. remove duplicated/transient reasoning.

## Fresh-session recovery

```text
root AGENTS.md
-> nearest scoped AGENTS.md
-> smallest applicable Skill
-> active plan when current execution state matters
-> minimal canonical working set
```

Do not reload historical baselines or all process documents by default.

## Branch discipline

Ordinary work happens on a branch and is integrated through a coherent PR. `main` represents curated accepted repository state.

If implementation exposes an upstream semantic problem, stop the affected slice, preserve useful WIP, record the finding and return to the owning Requirements/Domain/Architecture layer before continuing.
