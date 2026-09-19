# Engineering Graph v0 pilot

This branch evaluates the experimental producer/consumer Engineering Graph from
`lehater/harness` without changing Nutrition Management main or the existing
Harness pilot branch.

`.harness/engineering-graph.yaml` declares Authority production contracts and
terminal consumers. Existing `.harness/graph.yaml` remains the accepted Core
knowledge state during the experiment.

The derived targets are compared with current known behavior:

- IMPLEMENTATION -> COMPLETE;
- empty implementation target -> root Problem CREATE;
- accepted Problem only -> Requirements CREATE;
- theoretical gap suggestions -> COMPLETE;
- nutrient evidence propagation -> COMPLETE;
- BLS production import -> SOURCE-CODE-SET CREATE with downstream PENDING.

The experiment is intentionally separate from main and from the existing
`pilot/harness-managed-workspace` branch.
