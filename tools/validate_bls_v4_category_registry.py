from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from nutrition_management.food_knowledge.domain.model import TOP_LEVEL_CATEGORIES

SOURCE_VERSION = "4.0"
PRODUCTION_FOOD_COUNT = 7140


class CategoryRegistryError(ValueError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CategoryRegistryError(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CategoryRegistryError(f"{path} must contain a JSON object")
    return value


def _validate_source_codes(
    source: dict[str, Any],
    *,
    expected_count: int,
) -> tuple[str, ...]:
    if source.get("source_version") != SOURCE_VERSION:
        raise CategoryRegistryError(f"source_version must be {SOURCE_VERSION}")
    codes = source.get("source_codes")
    if not isinstance(codes, list) or any(not isinstance(code, str) or not code for code in codes):
        raise CategoryRegistryError("source_codes must be non-empty strings")
    if len(codes) != expected_count:
        raise CategoryRegistryError(
            f"source code count must be {expected_count}, got {len(codes)}"
        )
    if len(codes) != len(set(codes)):
        raise CategoryRegistryError("source_codes must be unique")
    return tuple(codes)


def validate_category_registry(
    source: dict[str, Any],
    registry: dict[str, Any],
    *,
    expected_count: int = PRODUCTION_FOOD_COUNT,
) -> None:
    source_codes = _validate_source_codes(source, expected_count=expected_count)

    if registry.get("source_version") != SOURCE_VERSION:
        raise CategoryRegistryError(f"registry source_version must be {SOURCE_VERSION}")
    mappings = registry.get("mappings")
    if not isinstance(mappings, list):
        raise CategoryRegistryError("registry mappings must be a list")

    mapped: dict[str, str] = {}
    ordered_codes: list[str] = []
    for index, item in enumerate(mappings):
        field = f"mappings[{index}]"
        if not isinstance(item, dict) or set(item) != {"source_code", "category"}:
            raise CategoryRegistryError(
                f"{field} must contain exactly source_code and category"
            )
        source_code = item.get("source_code")
        category = item.get("category")
        if not isinstance(source_code, str) or not source_code:
            raise CategoryRegistryError(f"{field}.source_code must be a non-empty string")
        if not isinstance(category, str) or category not in TOP_LEVEL_CATEGORIES:
            raise CategoryRegistryError(
                f"{field}.category must be an accepted ADR-005 top-level category"
            )
        if source_code in mapped:
            raise CategoryRegistryError(f"duplicate category mapping for {source_code}")
        mapped[source_code] = category
        ordered_codes.append(source_code)

    if ordered_codes != sorted(ordered_codes):
        raise CategoryRegistryError("registry mappings must be sorted by source_code")

    source_set = set(source_codes)
    mapped_set = set(mapped)
    if mapped_set != source_set:
        missing = sorted(source_set - mapped_set)
        extra = sorted(mapped_set - source_set)
        raise CategoryRegistryError(
            f"category registry must cover source codes exactly; missing={missing}, extra={extra}"
        )


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
