# Nutrition Management Full Design Pass

Status: accepted design baseline for the redesign branch.

This pass redesigns Nutrition Management from accepted problem evidence through Implementation Design without consulting implementation code and without authorizing code changes.

## Design rule

Existing product/domain/source documents are treated as prior design evidence. Decisions are re-accepted here only when they remain justified by the problem, requirements, source semantics and upstream contracts. Existing implementation is explicitly not evidence.

## Result

The redesign retains the four semantic Bounded Contexts because each owns an independently changing language and policy:

- Nutrition Targeting — what nutritional demand means for the household;
- Food Knowledge — what foods mean nutritionally;
- Market Catalog — what can be purchased and under which commercial conditions;
- Purchase Planning — what basket should be recommended.

The implementation-facing design is deliberately technology-neutral until Implementation Design. Component Design fixes responsibilities, contracts and dependency ownership; Implementation Design fixes the first implementation realization.

## Canonical redesign chain

Problem / Evidence → Product Scope → Requirements → Strategic Domain → Tactical Domain → Quality/Security → System Architecture → Application/Data/Interface Design → Engineering Policy → Component Design → Verification Design → Implementation Design → IMPLEMENTATION.

See `design-review.md` for the revalidation record and `implementation-design.md` for the terminal pre-code artifact.


