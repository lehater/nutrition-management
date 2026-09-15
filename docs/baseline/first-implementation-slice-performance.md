# First implementation slice — performance baseline

Status: historical completion evidence, not an SLA.
Date: 2026-09-15.
Implementation PR: #7 (`impl/first-planning-slice`).
Measured commit: `c6453c218d6a2ca273ca299b9a589fc1e13cf8e4`.
GitHub Actions run: `35016004825` (CI run #148), conclusion `success`.
Artifact: `solver-performance`, artifact id `10416110101`, SHA-256 `8ab8b14aa01480facb8915e6ec6f07d0de31e262057cbe259032e24deb8e7ad8`.

## Runtime environment

- Python: 3.14.7
- PySCIPOpt: 6.2.1
- SCIP: 10.0.2
- runner OS: Linux / x86_64
- logical CPU count reported by runner: 4
- platform: `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`

The same CI run passed the locked-environment check, full pytest suite, solver performance characterization and artifact upload before this baseline was recorded.

## Synthetic benchmark cases

| Offers / Base Foods | Mapped target dimensions | Sequential stages | Max variables | Max constraints | Selected lines | Final status | Wall time |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 16 | 5 | 45 | 185 | 294 | 13 | `policy_optimal` | 14.785100 s |
| 32 | 5 | 77 | 329 | 534 | 24 | `policy_optimal` | 50.462863 s |

Every recorded sequential optimization stage returned `optimal`. The benchmark intentionally exercises the production sequential objective order, including the exact technical total order over package and planned-quantity variables.

## Interpretation

This evidence is sufficient for the bounded first implementation slice: the accepted policy can execute deterministically on the target stack and each sequential stage proves optimality before the next stage is fixed.

It also confirms a non-blocking **P2 scalability risk**: exact technical lexicographic tie resolution adds two sequential stages per Offer and dominates runtime as candidate count grows. The 32-Offer synthetic case is already materially slower than the acceptance-scale case. Do not treat these numbers as a production latency target or extrapolate them linearly.

Before materially enlarging the executable catalog or introducing a user-facing latency expectation, re-characterize the solver and evaluate whether the technical total-order implementation can be optimized without changing ADR-007 business semantics or determinism.
