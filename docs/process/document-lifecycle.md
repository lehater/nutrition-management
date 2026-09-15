# Document and knowledge lifecycle

## Purpose

Define how Nutrition Management knowledge moves from discussion/evidence into durable accepted repository truth, and how that truth is changed without turning `docs/` into an archive dump.

## Core model

```text
conversation / research / code finding
        |
        v
classified evidence + proposals + unknowns
        |
        v
accepted by the owning semantic layer
        |
        v
living canonical artifact
        |
        +--> ADR when durable rationale is consequential
        +--> baseline only when an explicit milestone snapshot is useful
        +--> Git history as the normal historical archive
```

## Document roles

### Living canonical artifact

Represents current accepted truth. It may evolve when an owning decision changes.

Examples:
- current requirements;
- current Strategic/Tactical DDD;
- current architecture constraints.

Do not append old versions merely for history. Git already records them.

### ADR

Represents a consequential accepted choice plus rationale and consequences.

After acceptance, do not silently rewrite the decision/rationale to represent a new choice. Supersede it with a new ADR and link both directions when practical. Minor factual/format corrections are allowed when they do not change the decision.

### Active execution artifact

Represents resumable current work, not product truth. `docs/plans/active/README.md` should stay compact and point to canonical artifacts rather than duplicating them.

When work completes, absorb durable outcomes into canonical owners and remove stale execution material. Git history preserves it.

### Baseline/provenance artifact

Represents an intentionally retained historical snapshot or migration/provenance packet. Create one only when later comparison/audit/migration has demonstrated value. Baseline is not a second source of current truth.

## Status vocabulary

Use status labels only when they improve clarity:

- `draft` — working material, non-authoritative;
- `accepted` — current canonical truth at its owning layer;
- `superseded` — retained only when durable history/rationale is useful (normally ADR/baseline); otherwise rely on Git history.

A file without an explicit status is not automatically accepted; acceptance follows its owner and repository history/decision context.

## Fixation rule

Knowledge is considered fixed enough for downstream reliance when:

1. its semantic owner is identified;
2. blocking unknown/conflict is resolved or explicitly deferred as non-blocking;
3. the accepted statement is written in the smallest canonical owner;
4. consequential rationale is captured in an ADR when needed;
5. the change is versioned in Git through the normal review/integration path.

A baseline snapshot is not required for ordinary fixation.

## Change propagation

When accepted truth changes:

1. update the highest affected canonical owner first;
2. identify downstream artifacts that depend on the changed guarantee;
3. revalidate only those dependants;
4. update links/contracts that materially changed;
5. supersede ADRs explicitly when the decision itself changed;
6. do not copy the same invariant into every downstream document.

## What not to persist

Do not keep, by default:
- full chat transcripts;
- rejected brainstorming;
- duplicated explanations already owned canonically elsewhere;
- temporary analysis reports after their accepted conclusions are absorbed;
- obsolete plans solely for history.

Persist unresolved material questions only when losing them would harm future work, and place them in the smallest current owner.
