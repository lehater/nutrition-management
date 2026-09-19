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


def _category(value: object, field: str) -> str:
    if not isinstance(value, str) or value not in TOP_LEVEL_CATEGORIES:
        raise CategoryRegistryError(
            f"{field} must be an accepted ADR-005 top-level category"
        )
    return value


def resolve_category_registry(
    source: dict[str, Any],
    registry: dict[str, Any],
    *,
    expected_count: int = PRODUCTION_FOOD_COUNT,
) -> dict[str, str]:
    source_codes = _validate_source_codes(source, expected_count=expected_count)

    if registry.get("source_version") != SOURCE_VERSION:
        raise CategoryRegistryError(f"registry source_version must be {SOURCE_VERSION}")

    rules = registry.get("rules")
    overrides = registry.get("overrides", [])
    if not isinstance(rules, list) or not rules:
        raise CategoryRegistryError("registry rules must be a non-empty list")
    if not isinstance(overrides, list):
        raise CategoryRegistryError("registry overrides must be a list")

    parsed_rules: list[tuple[str, str]] = []
    seen_prefixes: set[str] = set()
    for index, item in enumerate(rules):
        field = f"rules[{index}]"
        if not isinstance(item, dict) or set(item) != {"prefix", "category"}:
            raise CategoryRegistryError(
                f"{field} must contain exactly prefix and category"
            )
        prefix = item.get("prefix")
        if not isinstance(prefix, str) or not prefix:
            raise CategoryRegistryError(f"{field}.prefix must be a non-empty string")
        if prefix in seen_prefixes:
            raise CategoryRegistryError(f"duplicate prefix rule for {prefix}")
        seen_prefixes.add(prefix)
        parsed_rules.append((prefix, _category(item.get("category"), f"{field}.category")))

    if [prefix for prefix, _ in parsed_rules] != sorted(prefix for prefix, _ in parsed_rules):
        raise CategoryRegistryError("registry rules must be sorted by prefix")

    parsed_overrides: dict[str, str] = {}
    ordered_override_codes: list[str] = []
    source_set = set(source_codes)
    for index, item in enumerate(overrides):
        field = f"overrides[{index}]"
        if not isinstance(item, dict) or set(item) != {"source_code", "category"}:
            raise CategoryRegistryError(
                f"{field} must contain exactly source_code and category"
            )
        source_code = item.get("source_code")
        if not isinstance(source_code, str) or not source_code:
            raise CategoryRegistryError(f"{field}.source_code must be a non-empty string")
        if source_code not in source_set:
            raise CategoryRegistryError(f"{field}.source_code is not in the pinned source set")
        if source_code in parsed_overrides:
            raise CategoryRegistryError(f"duplicate exact override for {source_code}")
        parsed_overrides[source_code] = _category(
            item.get("category"), f"{field}.category"
        )
        ordered_override_codes.append(source_code)

    if ordered_override_codes != sorted(ordered_override_codes):
        raise CategoryRegistryError("registry overrides must be sorted by source_code")

    matched_by_rule = {prefix: 0 for prefix, _ in parsed_rules}
    resolved: dict[str, str] = {}
    for source_code in source_codes:
        override = parsed_overrides.get(source_code)
        if override is not None:
            resolved[source_code] = override
            continue

        matches = [
            (prefix, category)
            for prefix, category in parsed_rules
            if source_code.startswith(prefix)
        ]
        if not matches:
            raise CategoryRegistryError(
                f"BLS source code has no category decision: {source_code}"
            )
        if len(matches) > 1:
            raise CategoryRegistryError(
                f"BLS source code matches multiple prefix rules: "
                f"{source_code} -> {[prefix for prefix, _ in matches]}"
            )
        prefix, category = matches[0]
        matched_by_rule[prefix] += 1
        resolved[source_code] = category

    unused = sorted(prefix for prefix, count in matched_by_rule.items() if count == 0)
    if unused:
        raise CategoryRegistryError(f"prefix rules match no non-overridden source codes: {unused}")

    return dict(sorted(resolved.items()))


def validate_category_registry(
    source: dict[str, Any],
    registry: dict[str, Any],
    *,
    expected_count: int = PRODUCTION_FOOD_COUNT,
) -> None:
    resolved = resolve_category_registry(
        source,
        registry,
        expected_count=expected_count,
    )
    if len(resolved) != expected_count:
        raise CategoryRegistryError(
            f"resolved category count must be {expected_count}, got {len(resolved)}"
        )
