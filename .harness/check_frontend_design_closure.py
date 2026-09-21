#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / "docs/interface/frontend-presentation-system.yaml"
SCREENS = ROOT / "docs/interface/frontend-screen-view-design.yaml"

def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def main() -> int:
    errors = []
    presentation = load(PRESENTATION)
    screen_design = load(SCREENS)

    expected = presentation.get("scope", {}).get("screens", []) or []
    screens = screen_design.get("screens", []) or []
    actual = [screen.get("id") for screen in screens]
    coverage = screen_design.get("coverage", {}).get("required_screens", []) or []

    if len(actual) != len(set(actual)):
        errors.append("duplicate screen ids in Screen/View contract")
    if set(actual) != set(expected):
        errors.append(
            f"Presentation System scope and Screen/View inventory differ: "
            f"missing={sorted(set(expected)-set(actual))} extra={sorted(set(actual)-set(expected))}"
        )
    if set(coverage) != set(expected):
        errors.append("coverage.required_screens must equal Presentation System screen scope")
    if screen_design.get("inherits") != presentation.get("id"):
        errors.append("Screen/View contract does not inherit the canonical Presentation System")

    patterns = set((presentation.get("patterns") or {}).keys())
    for screen in screens:
        sid = screen.get("id", "<unknown>")
        for required in ("purpose", "regions", "states", "overrides"):
            if required not in screen:
                errors.append(f"{sid}: missing {required}")
        for pattern in screen.get("patterns", []) or []:
            if pattern not in patterns:
                errors.append(f"{sid}: unknown pattern {pattern}")

    if errors:
        print("Frontend design closure failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        f"Frontend design closure PASS: {len(actual)} screens inherit "
        f"{presentation.get('id')}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
