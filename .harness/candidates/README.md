# BLS 4.0 category registry candidate

Status: candidate only; not canonical and not registered in the Harness Core graph.

Purpose: exercise the `source-classification-registry` skill using only classifications that are straightforward under the accepted ADR-005 taxonomy and the published BLS hierarchy.

The candidate intentionally leaves mixed or policy-sensitive BLS groups unresolved rather than guessing.

Known unresolved prefix families include at least:

- `D` — fine bakery/pastry products;
- `E0`, `E3`, `E9` — mixed/other egg and pasta groups;
- `J` — vegetarian products spanning multiple project categories;
- `L` — foods for special nutrition;
- `P` — alcoholic beverages, whose treatment under the project variety taxonomy needs explicit review;
- `R` — recipe ingredients/seasonings/additives;
- `S` — sweets and confectionery;
- `X` and `Y` — prepared menu components spanning multiple food groups.

The exact unresolved set must be calculated against the pinned BLS 4.0 source-code baseline generated from the official main workbook. Until that baseline is available and the candidate resolves every code exactly once, this file must not provide `nutrition-management.food-knowledge.bls-v4.category-assignment`.
