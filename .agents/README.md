# Nutrition Management repository agent harness

The harness is intentionally repository-local and small.

A fresh session starts from `AGENTS.md`, loads the smallest applicable Skill, then reads only the project truth required by the task. `docs/plans/active/README.md` is loaded when current execution state matters.

Conversation history is disposable. Durable accepted knowledge, unresolved material decisions and resumable execution state live in the repository.

## Responsibility split

- `AGENTS.md` — routing and persistent guardrails.
- `.agents/skills/` — judgement-heavy reusable workflows.
- `docs/process/` — protocols shared by several Skills/humans.
- `docs/domain|requirements|architecture|decisions/` — project truth.
- `docs/plans/active/README.md` — compact resume state.
- `tools/` — deterministic harness checks.

Do not add multi-agent orchestration, runtime state machines or overlapping Skills until a demonstrated workflow requires them.
