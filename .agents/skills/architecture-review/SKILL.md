---
name: architecture-review
description: "Use to critically review Nutrition Management architecture or implementation against accepted domain ownership, ADRs, Clean Architecture dependency direction and the smallest justified design. Produce P0-P3 findings without inventing upstream product/domain decisions."
---

# Architecture Review

Review through these lenses:

1. semantic ownership and `Bounded Context != service/database/deployment`;
2. dependency direction and explicit boundary ownership;
3. domain invariants, identity and lifecycle preservation;
4. consistency/data ownership and bypass risks;
5. external-seam semantics, errors and temporal behavior where material;
6. unnecessary infrastructure, distribution or abstraction;
7. consistency with accepted ADRs and requirements.

For each material finding state:
- priority P0-P3;
- violated accepted contract/invariant;
- concrete evidence/path;
- owning lifecycle layer;
- smallest corrective action.

If the fix requires missing product behavior, reopen Requirements. If it requires missing/wrong semantic ownership, reopen Domain Design. Do not hide upstream uncertainty inside an architecture workaround.
