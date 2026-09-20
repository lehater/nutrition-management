# Nutrition Management — Human Documentation

> Generated projection from accepted canonical project knowledge. Do not edit this directory as a source of truth.

Projection baseline: Nutrition Management `main` after current-Harness conformance; selected Harness Consumer: `IMPLEMENTATION`.

## What the system is

Nutrition Management is an advisory application that produces one executable 30-day household purchase recommendation balancing nutritional coverage, variety, acquisition cost and procurement simplicity while preserving uncertainty and provenance.

The MVP is deliberately narrower than a diet/medical/meal-planning platform. It does not own therapeutic diets, allergies, consumption tracking, recipes, inventory, saved plan history, FX conversion or personalized promotions.

Canonical sources: `docs/requirements/product-requirements.md`.

## How to read this projection

- [System overview](overview.md) — scope, architecture and primary flow.
- [Domain and data](domain-and-data.md) — semantic ownership, evidence/provenance and temporal rules.
- [Implementation guide](implementation-guide.md) — accepted realization and coding boundaries.
- [Verification and readiness](verification-and-readiness.md) — required proof, cross-cutting coverage and reopening conditions.

The canonical engineering sources remain the project documents referenced in each generated section plus `.harness/engineering-graph.yaml` and `.harness/graph.yaml`.

Deleting this directory must not change Harness target state.
