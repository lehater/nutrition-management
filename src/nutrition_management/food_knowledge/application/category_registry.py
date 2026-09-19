from __future__ import annotations

from typing import Any

from nutrition_management.food_knowledge.domain.model import TOP_LEVEL_CATEGORIES

SOURCE_VERSION = "4.0"
PRODUCTION_FOOD_COUNT = 7140


class CategoryRegistryError(ValueError):
    pass


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
