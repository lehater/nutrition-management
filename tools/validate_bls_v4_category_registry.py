from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from nutrition_management.food_knowledge.application.category_registry import (
    CategoryRegistryError,
    PRODUCTION_FOOD_COUNT,
    validate_category_registry,
)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CategoryRegistryError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CategoryRegistryError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the explicit BLS 4.0 -> ADR-005 category registry"
    )
    parser.add_argument("source_codes", type=Path)
    parser.add_argument("registry", type=Path)
    parser.add_argument(
        "--expected-count",
        type=int,
        default=PRODUCTION_FOOD_COUNT,
        help="expected BLS food-code count; production default is 7140",
    )
    args = parser.parse_args()

    validate_category_registry(
        _load_json(args.source_codes),
        _load_json(args.registry),
        expected_count=args.expected_count,
    )
    print(
        f"BLS 4.0 category registry validation passed "
        f"({args.expected_count} exact assignments)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
