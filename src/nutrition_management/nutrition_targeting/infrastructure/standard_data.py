from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from pathlib import Path

from nutrition_management.nutrition_targeting.domain.model import (
    AgeBoundary,
    AgeUnit,
    ApplicableWeightRule,
    ApplicabilityRequirement,
    MappingStatus,
    NutritionStandardSet,
    ReferenceApplicability,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceKind,
    ReferenceScope,
    SafetyDefinition,
    SafetySemanticKind,
    Sex,
    SourceSemanticKind,
    TargetMapping,
)
from nutrition_management.nutrition_targeting.infrastructure.repository import NutritionTargetingRepository

_REQUIRED_FILES = ("references.json", "safety_limits.json", "mappings.json")

# Keys reflect the current DGE reference-value overview. A production package must
# account for each topic without inventing a numeric reference where DGE has none.
MVP_V1_DGE_TOPICS = frozenset(
    {
        "energy",
        "protein",
        "fat_and_essential_fatty_acids",
        "carbohydrates",
        "fibre",
        "alcohol",
        "water",
        "vitamin_a",
        "vitamin_d",
        "vitamin_e",
        "vitamin_k",
        "thiamin",
        "riboflavin",
        "niacin",
        "vitamin_b6",
        "folate",
        "pantothenic_acid",
        "biotin",
        "vitamin_b12",
        "vitamin_c",
        "sodium",
        "chloride",
        "potassium",
        "calcium",
        "phosphorus",
        "magnesium",
        "iron",
        "iodine",
        "fluoride",
        "zinc",
        "selenium",
        "copper",
        "chromium",
        "manganese",
        "molybdenum",
    }
)


@dataclass(frozen=True)
class LoadedStandardPackage:
    standard: NutritionStandardSet
    manifest_json: str
    package_digest: str


class StandardPackageError(ValueError):
    pass


def _canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_file(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StandardPackageError(f"cannot read valid JSON from {path.name}: {exc}") from exc


def _digest_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def compute_manifest_digest(manifest: dict) -> str:
    payload = dict(manifest)
    payload.pop("package_digest", None)
    return _digest_bytes(_canonical_json(payload).encode("utf-8"))


def _decimal(value, field: str) -> Decimal | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise StandardPackageError(f"{field} must be a decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise StandardPackageError(f"{field} is not a decimal: {value}") from exc
    if not parsed.is_finite():
        raise StandardPackageError(f"{field} must be finite")
    return parsed


def _required_text(value, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise StandardPackageError(f"{field} must be a non-empty string")
    return value


def _boundary(value, field: str) -> AgeBoundary | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise StandardPackageError(f"{field} must be an object")
    raw_value = value.get("value")
    if not isinstance(raw_value, int):
        raise StandardPackageError(f"{field}.value must be an integer")
    try:
        return AgeBoundary(raw_value, AgeUnit(value.get("unit")))
    except (ValueError, TypeError) as exc:
        raise StandardPackageError(f"invalid {field}: {exc}") from exc


def _applicability(value, field: str) -> ReferenceApplicability:
    if value is None:
        return ReferenceApplicability()
    if not isinstance(value, dict):
        raise StandardPackageError(f"{field} must be an object")
    requirements = value.get("requirements", [])
    if not isinstance(requirements, list):
        raise StandardPackageError(f"{field}.requirements must be an array")
    try:
        return ReferenceApplicability(
            min_age=_boundary(value.get("min_age"), f"{field}.min_age"),
            max_age=_boundary(value.get("max_age"), f"{field}.max_age"),
            sex=None if value.get("sex") is None else Sex(value["sex"]),
            requirements=tuple(
                ApplicabilityRequirement(
                    _required_text(item.get("dimension"), f"{field}.requirements.dimension"),
                    _required_text(item.get("value"), f"{field}.requirements.value"),
                )
                for item in requirements
            ),
        )
    except (ValueError, TypeError, AttributeError) as exc:
        raise StandardPackageError(f"invalid {field}: {exc}") from exc


def _reference(row: dict, index: int, source_ids: set[str]) -> ReferenceDefinition:
    field = f"references.rows[{index}]"
    if not isinstance(row, dict):
        raise StandardPackageError(f"{field} must be an object")
    source_id = _required_text(row.get("source_id"), f"{field}.source_id")
    if source_id not in source_ids:
        raise StandardPackageError(f"{field}.source_id references unknown source {source_id}")
    try:
        return ReferenceDefinition(
            reference_id=_required_text(row.get("row_id"), f"{field}.row_id"),
            family_id=_required_text(row.get("family_id"), f"{field}.family_id"),
            nutrient_measure=_required_text(row.get("nutrient_measure"), f"{field}.nutrient_measure"),
            kind=ReferenceKind(row.get("target_kind")),
            basis=ReferenceBasis(row.get("basis")),
            lower=_decimal(row.get("lower"), f"{field}.lower"),
            upper=_decimal(row.get("upper"), f"{field}.upper"),
            point=_decimal(row.get("point"), f"{field}.point"),
            energy_kcal_per_g=_decimal(row.get("energy_kcal_per_g"), f"{field}.energy_kcal_per_g"),
            source_semantic_kind=SourceSemanticKind(row.get("source_semantic_kind")),
            source_unit=_required_text(row.get("source_unit"), f"{field}.source_unit"),
            scope=ReferenceScope(row.get("scope", ReferenceScope.ACTIVE.value)),
            applicability=_applicability(row.get("applicability"), f"{field}.applicability"),
            applicable_weight_rule=None
            if row.get("applicable_weight_rule") is None
            else ApplicableWeightRule(row["applicable_weight_rule"]),
            source_id=source_id,
            source_locator=_required_text(row.get("source_locator"), f"{field}.source_locator"),
        )
    except (ValueError, TypeError) as exc:
        raise StandardPackageError(f"invalid {field}: {exc}") from exc


def _mapping(row: dict, index: int) -> TargetMapping:
    field = f"mappings.mappings[{index}]"
    if not isinstance(row, dict):
        raise StandardPackageError(f"{field} must be an object")
    try:
        return TargetMapping(
            family_id=_required_text(row.get("family_id"), f"{field}.family_id"),
            status=MappingStatus(row.get("status")),
            nutrient_measure=row.get("nutrient_measure"),
            canonical_unit=row.get("canonical_unit"),
            formula_id=row.get("formula_id"),
            reason=row.get("reason"),
        )
    except (ValueError, TypeError) as exc:
        raise StandardPackageError(f"invalid {field}: {exc}") from exc


def _safety(row: dict, index: int, source_ids: set[str]) -> SafetyDefinition:
    field = f"safety_limits.rows[{index}]"
    if not isinstance(row, dict):
        raise StandardPackageError(f"{field} must be an object")
    source_id = _required_text(row.get("source_id"), f"{field}.source_id")
    if source_id not in source_ids:
        raise StandardPackageError(f"{field}.source_id references unknown source {source_id}")
    try:
        daily_upper = _decimal(row.get("daily_upper"), f"{field}.daily_upper")
        if daily_upper is None:
            raise StandardPackageError(f"{field}.daily_upper is required")
        return SafetyDefinition(
            reference_id=_required_text(row.get("row_id"), f"{field}.row_id"),
            family_id=_required_text(row.get("family_id"), f"{field}.family_id"),
            nutrient_measure=_required_text(row.get("nutrient_measure"), f"{field}.nutrient_measure"),
            daily_upper=daily_upper,
            semantic_kind=SafetySemanticKind(row.get("semantic_kind", SafetySemanticKind.UL.value)),
            source_unit=_required_text(row.get("source_unit"), f"{field}.source_unit"),
            scope=ReferenceScope(row.get("scope", ReferenceScope.ACTIVE.value)),
            applicability=_applicability(row.get("applicability"), f"{field}.applicability"),
            substance_scope=_required_text(row.get("substance_scope"), f"{field}.substance_scope"),
            source_id=source_id,
            source_locator=_required_text(row.get("source_locator"), f"{field}.source_locator"),
        )
    except (ValueError, TypeError) as exc:
        if isinstance(exc, StandardPackageError):
            raise
        raise StandardPackageError(f"invalid {field}: {exc}") from exc


def _validate_mvp_v1_manifest(manifest: dict) -> None:
    accounting = manifest.get("topic_accounting")
    if not isinstance(accounting, dict):
        raise StandardPackageError("mvp-v1 manifest requires topic_accounting")
    keys = set(accounting)
    if keys != MVP_V1_DGE_TOPICS:
        missing = sorted(MVP_V1_DGE_TOPICS - keys)
        extra = sorted(keys - MVP_V1_DGE_TOPICS)
        raise StandardPackageError(f"mvp-v1 topic_accounting mismatch; missing={missing}, extra={extra}")
    alcohol = accounting["alcohol"]
    if not isinstance(alcohol, dict) or alcohol.get("status") != "non_active":
        raise StandardPackageError("mvp-v1 alcohol topic must be explicitly non_active")


def load_standard_package(directory: Path) -> LoadedStandardPackage:
    manifest_path = directory / "manifest.json"
    manifest = _json_file(manifest_path)
    if not isinstance(manifest, dict):
        raise StandardPackageError("manifest must be an object")

    version = _required_text(manifest.get("standard_version"), "manifest.standard_version")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise StandardPackageError("manifest.sources must be a non-empty array")
    source_ids = {
        _required_text(item.get("id"), "manifest.sources.id")
        for item in sources
        if isinstance(item, dict)
    }
    if len(source_ids) != len(sources):
        raise StandardPackageError("manifest sources must be objects with unique ids")

    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != set(_REQUIRED_FILES):
        raise StandardPackageError(f"manifest.files must contain exactly {list(_REQUIRED_FILES)}")
    for name in _REQUIRED_FILES:
        path = directory / name
        try:
            actual = _digest_bytes(path.read_bytes())
        except OSError as exc:
            raise StandardPackageError(f"cannot read package file {name}: {exc}") from exc
        if files[name] != actual:
            raise StandardPackageError(f"digest mismatch for {name}")

    expected_package_digest = _required_text(manifest.get("package_digest"), "manifest.package_digest")
    actual_package_digest = compute_manifest_digest(manifest)
    if expected_package_digest != actual_package_digest:
        raise StandardPackageError("manifest package_digest does not match canonical manifest content")

    if version == "mvp-v1":
        _validate_mvp_v1_manifest(manifest)

    references_raw = _json_file(directory / "references.json")
    safety_raw = _json_file(directory / "safety_limits.json")
    mappings_raw = _json_file(directory / "mappings.json")
    if not isinstance(references_raw, dict) or not isinstance(references_raw.get("rows"), list):
        raise StandardPackageError("references.json requires rows array")
    if not isinstance(safety_raw, dict) or not isinstance(safety_raw.get("rows"), list):
        raise StandardPackageError("safety_limits.json requires rows array")
    if not isinstance(mappings_raw, dict) or not isinstance(mappings_raw.get("mappings"), list):
        raise StandardPackageError("mappings.json requires mappings array")

    standard = NutritionStandardSet(
        version=version,
        content_digest=actual_package_digest,
        references=tuple(_reference(row, index, source_ids) for index, row in enumerate(references_raw["rows"])),
        safety_limits=tuple(_safety(row, index, source_ids) for index, row in enumerate(safety_raw["rows"])),
        mappings=tuple(_mapping(row, index) for index, row in enumerate(mappings_raw["mappings"])),
    )
    if version == "mvp-v1" and not standard.mappings:
        raise StandardPackageError("mvp-v1 requires a complete mapping decision registry")

    return LoadedStandardPackage(
        standard=standard,
        manifest_json=_canonical_json(manifest),
        package_digest=actual_package_digest,
    )


def import_standard_package(
    repository: NutritionTargetingRepository,
    package: LoadedStandardPackage,
    *,
    active: bool = False,
) -> str:
    version = package.standard.version
    if repository.standard_exists(version):
        existing_digest = repository.standard_digest(version)
        if existing_digest != package.package_digest:
            raise StandardPackageError(
                f"immutable standard version {version} already exists with different content"
            )
        if active:
            repository.activate_standard(version)
        return "unchanged"

    repository.add_standard(
        package.standard,
        active=active,
        source_manifest=package.manifest_json,
    )
    return "inserted"
