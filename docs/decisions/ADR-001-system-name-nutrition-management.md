# ADR-001 — System name Nutrition Management

Status: `accepted`.

Date: 2026-09-15.

## Context

The repository needs one unambiguous product/system name that can be referenced independently from future Bounded Context names and implementation package names.

## Decision

Use **Nutrition Management** as the product/system name.

Use `nutrition-management` as the repository name.

Future Bounded Contexts receive semantic names derived from domain ownership. They are not automatically named after the whole product.

## Consequences

- Nutrition Management denotes the whole product/system.
- Domain boundaries remain to be discovered and accepted independently.
- The repository bootstrap does not imply any concrete service/package/module topology.
