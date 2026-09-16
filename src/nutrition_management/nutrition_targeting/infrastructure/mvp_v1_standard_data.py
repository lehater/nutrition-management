from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

from nutrition_management.nutrition_targeting.domain.model import MappingStatus, SafetyMapping
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


def load_mvp_v1_standard_package(directory: Path) -> LoadedStandardPackage:
    loaded = load_standard_package(directory)
    if loaded.standard.version != "mvp-v1":
        raise StandardPackageError("production loader requires standard_version mvp-v1")

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
