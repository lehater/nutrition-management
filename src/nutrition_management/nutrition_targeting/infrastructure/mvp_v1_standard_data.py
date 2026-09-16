from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
import json
from pathlib import Path

from nutrition_management.nutrition_targeting.domain.model import (
    AgeUnit,
    MappingStatus,
    ReferenceScope,
    SafetyMapping,
)
from nutrition_management.nutrition_targeting.infrastructure.standard_data import (
    LoadedStandardPackage,
    StandardPackageError,
    load_standard_package,
)


def _required_text(value, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise StandardPackageError(f"{field} must be a non-empty string")
    return value


def _safety_mapping(row: dict, index: int) -> SafetyMapping:
    field = f"mappings.safety_mappings[{index}]"
    if not isinstance(row, dict):
        raise StandardPackageError(f"{field} must be an object")
    try:
        return SafetyMapping(
            family_id=_required_text(row.get("family_id"), f"{field}.family_id"),
            status=MappingStatus(row.get("status")),
            nutrient_measure=row.get("nutrient_measure"),
            canonical_unit=row.get("canonical_unit"),
            reason=row.get("reason"),
        )
    except (TypeError, ValueError) as exc:
        raise StandardPackageError(f"invalid {field}: {exc}") from exc


def _age_month(boundary, *, default: int | None) -> int | None:
    if boundary is None:
        return default
    multiplier = 12 if boundary.unit == AgeUnit.YEARS else 1
    return boundary.value * multiplier


def _applicability_can_overlap(left, right) -> bool:
    if left.sex is not None and right.sex is not None and left.sex != right.sex:
        return False

    left_requirements = {item.dimension: item.value for item in left.requirements}
    right_requirements = {item.dimension: item.value for item in right.requirements}
    for dimension in left_requirements.keys() & right_requirements.keys():
        if left_requirements[dimension] != right_requirements[dimension]:
            return False

    left_min = _age_month(left.min_age, default=0)
    right_min = _age_month(right.min_age, default=0)
    left_max = _age_month(left.max_age, default=None)
    right_max = _age_month(right.max_age, default=None)
    lower = max(left_min, right_min)
    upper_candidates = [value for value in (left_max, right_max) if value is not None]
    upper = min(upper_candidates) if upper_candidates else None
    return upper is None or lower < upper


def _validate_deterministic_families(definitions, *, label: str) -> None:
    grouped = defaultdict(list)
    for item in definitions:
        if item.scope == ReferenceScope.ACTIVE:
            grouped[item.resolved_family_id].append(item)

    for family_id, rows in sorted(grouped.items()):
        ordered = sorted(rows, key=lambda item: item.reference_id)
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                if _applicability_can_overlap(left.applicability, right.applicability):
                    raise StandardPackageError(
                        f"{label} family {family_id} has ambiguous active source variants: "
                        f"{left.reference_id}, {right.reference_id}"
                    )


def load_mvp_v1_standard_package(directory: Path) -> LoadedStandardPackage:
    loaded = load_standard_package(directory)
    if loaded.standard.version != "mvp-v1":
        raise StandardPackageError("production loader requires standard_version mvp-v1")

    _validate_deterministic_families(loaded.standard.references, label="reference")
    _validate_deterministic_families(loaded.standard.safety_limits, label="safety")

    try:
        raw = json.loads((directory / "mappings.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StandardPackageError(f"cannot read mappings.json: {exc}") from exc
    rows = raw.get("safety_mappings") if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        raise StandardPackageError("mvp-v1 mappings.json requires safety_mappings array")

    safety_mappings = tuple(_safety_mapping(row, index) for index, row in enumerate(rows))
    active_safety = {item.resolved_family_id for item in loaded.standard.safety_limits if item.scope.value == "active"}
    if active_safety and not safety_mappings:
        raise StandardPackageError("mvp-v1 active safety limits require explicit safety mapping decisions")

    try:
        standard = replace(loaded.standard, safety_mappings=safety_mappings)
    except ValueError as exc:
        raise StandardPackageError(f"invalid mvp-v1 safety mapping registry: {exc}") from exc
    return replace(loaded, standard=standard)
