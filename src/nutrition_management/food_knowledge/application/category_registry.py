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


def analyze_category_registry(
    source: dict[str, Any],
    registry: dict[str, Any],
    *,
    expected_count: int = PRODUCTION_FOOD_COUNT,
) -> dict[str, Any]:
    source_codes = _validate_source_codes(source, expected_count=expected_count)

    if registry.get("source_version") != SOURCE_VERSION:
        raise CategoryRegistryError(f"registry source_version must be {SOURCE_VERSION}")

    rules = registry.get("rules")
    overrides = registry.get("overrides", [])
    if not isinstance(rules, list):
        raise CategoryRegistryError("registry rules must be a list")
    if not isinstance(overrides, list):
        raise CategoryRegistryError("registry overrides must be a list")

    parsed_rules: list[tuple[str, str]] = []
    seen_prefixes: set[str] = set()
    structural_errors: list[str] = []
    for index, item in enumerate(rules):
        field = f"rules[{index}]"
        if not isinstance(item, dict) or set(item) != {"prefix", "category"}:
            structural_errors.append(f"{field} must contain exactly prefix and category")
            continue
        prefix = item.get("prefix")
        if not isinstance(prefix, str) or not prefix:
            structural_errors.append(f"{field}.prefix must be a non-empty string")
            continue
        if prefix in seen_prefixes:
            structural_errors.append(f"duplicate prefix rule for {prefix}")
            continue
        seen_prefixes.add(prefix)
        try:
            category = _category(item.get("category"), f"{field}.category")
        except CategoryRegistryError as exc:
            structural_errors.append(str(exc))
            continue
        parsed_rules.append((prefix, category))

    parsed_overrides: dict[str, str] = {}
    source_set = set(source_codes)
    for index, item in enumerate(overrides):
        field = f"overrides[{index}]"
        if not isinstance(item, dict) or set(item) != {"source_code", "category"}:
            structural_errors.append(
                f"{field} must contain exactly source_code and category"
            )
            continue
        source_code = item.get("source_code")
        if not isinstance(source_code, str) or not source_code:
            structural_errors.append(f"{field}.source_code must be a non-empty string")
            continue
        if source_code not in source_set:
            structural_errors.append(
                f"{field}.source_code is not in the pinned source set"
            )
            continue
        if source_code in parsed_overrides:
            structural_errors.append(f"duplicate exact override for {source_code}")
            continue
        try:
            category = _category(item.get("category"), f"{field}.category")
        except CategoryRegistryError as exc:
            structural_errors.append(str(exc))
            continue
        parsed_overrides[source_code] = category

    matched_by_rule = {prefix: 0 for prefix, _ in parsed_rules}
    resolved: dict[str, str] = {}
    unmapped: list[str] = []
    ambiguous: dict[str, list[str]] = {}
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
            unmapped.append(source_code)
            continue
        if len(matches) > 1:
            ambiguous[source_code] = [prefix for prefix, _ in matches]
            continue
        prefix, category = matches[0]
        matched_by_rule[prefix] += 1
        resolved[source_code] = category

    unused_rules = sorted(
        prefix for prefix, count in matched_by_rule.items() if count == 0
    )
    return {
        "resolved_count": len(resolved),
        "resolved": dict(sorted(resolved.items())),
        "unmapped": sorted(unmapped),
        "ambiguous": dict(sorted(ambiguous.items())),
        "unused_rules": unused_rules,
        "structural_errors": structural_errors,
    }


def resolve_category_registry(
    source: dict[str, Any],
    registry: dict[str, Any],
    *,
    expected_count: int = PRODUCTION_FOOD_COUNT,
) -> dict[str, str]:
    rules = registry.get("rules")
    overrides = registry.get("overrides", [])
    if not isinstance(rules, list) or not rules:
        raise CategoryRegistryError("registry rules must be a non-empty list")
    if not isinstance(overrides, list):
        raise CategoryRegistryError("registry overrides must be a list")

    prefixes = [
        item.get("prefix")
        for item in rules
        if isinstance(item, dict)
    ]
    if prefixes != sorted(prefixes):
        raise CategoryRegistryError("registry rules must be sorted by prefix")
    override_codes = [
        item.get("source_code")
        for item in overrides
        if isinstance(item, dict)
    ]
    if override_codes != sorted(override_codes):
        raise CategoryRegistryError("registry overrides must be sorted by source_code")

    report = analyze_category_registry(
        source,
        registry,
        expected_count=expected_count,
    )
    if report["structural_errors"]:
        raise CategoryRegistryError("; ".join(report["structural_errors"]))
    if report["unmapped"]:
        raise CategoryRegistryError(
            f"BLS source code has no category decision: {report['unmapped'][0]}"
        )
    if report["ambiguous"]:
        source_code, prefixes = next(iter(report["ambiguous"].items()))
        raise CategoryRegistryError(
            f"BLS source code matches multiple prefix rules: {source_code} -> {prefixes}"
        )
    if report["unused_rules"]:
        raise CategoryRegistryError(
            f"prefix rules match no non-overridden source codes: {report['unused_rules']}"
        )

    return report["resolved"]


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
