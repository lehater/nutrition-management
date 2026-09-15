#!/usr/bin/env python3
"""Validate the minimal Nutrition Management repository-local harness."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---(?:\n|$)", re.DOTALL)
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

REQUIRED_FILES = [
    "AGENTS.md",
    ".agents/README.md",
    ".agents/skills/AGENTS.md",
    "docs/AGENTS.md",
    "docs/README.md",
    "docs/process/README.md",
    "docs/process/change-lifecycle.md",
    "docs/process/decision-protocol.md",
    "docs/process/document-lifecycle.md",
    "docs/process/domain-change-protocol.md",
    "docs/process/strategic-ddd-convergence.md",
    "docs/process/tactical-ddd-stage.md",
    "docs/process/working-loop.md",
    "docs/domain/README.md",
    "docs/domain/strategic-model.md",
    "docs/domain/context-map.md",
    "docs/requirements/README.md",
    "docs/architecture/README.md",
    "docs/decisions/README.md",
    "docs/decisions/ADR-000-template.md",
    "docs/plans/active/README.md",
]

REQUIRED_SKILLS = {
    "agent-harness-design",
    "architecture-review",
    "domain-model-change",
    "record-project-knowledge",
    "resolve-decision",
}


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_skill(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = FRONTMATTER.match(text)
    if not match:
        error(errors, f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    name = fields.get("name", "")
    description = fields.get("description", "")
    if name != path.parent.name or not NAME.fullmatch(name):
        error(errors, f"{path.relative_to(ROOT)}: invalid/mismatched skill name")
    if not description:
        error(errors, f"{path.relative_to(ROOT)}: description is required")


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            error(errors, f"missing required harness file: {relative}")

    if SKILLS.is_dir():
        actual = {p.parent.name for p in SKILLS.glob("*/SKILL.md")}
        missing = REQUIRED_SKILLS - actual
        for name in sorted(missing):
            error(errors, f"missing required skill: {name}")
        for path in sorted(SKILLS.glob("*/SKILL.md")):
            parse_skill(path, errors)
    else:
        error(errors, "missing .agents/skills directory")

    root_agents = ROOT / "AGENTS.md"
    if root_agents.is_file():
        text = root_agents.read_text(encoding="utf-8")
        for marker in [
            "docs/process/decision-protocol.md",
            "docs/process/document-lifecycle.md",
            "docs/process/domain-change-protocol.md",
            "Bounded Context is a semantic ownership boundary",
            "Do not commit ordinary agent work directly to `main`",
        ]:
            if marker not in text:
                error(errors, f"AGENTS.md missing guardrail marker: {marker}")

    strategic = ROOT / "docs/domain/strategic-model.md"
    if strategic.is_file():
        text = strategic.read_text(encoding="utf-8")
        if "No product Bounded Contexts are accepted yet" not in text:
            error(errors, "bootstrap strategic model must not invent accepted Bounded Contexts")

    adr = ROOT / "docs/decisions/ADR-001-system-name-nutrition-management.md"
    if adr.is_file() and "Status: `accepted`." not in adr.read_text(encoding="utf-8"):
        error(errors, "ADR-001 must record the accepted system name")

    if errors:
        print("Harness validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print("Harness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
