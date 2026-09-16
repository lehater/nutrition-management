from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import string

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.application.source_data import (
    ComponentDefinition,
    FoodSourceDataset,
    SourceFood,
    SourceNutrientEvidence,
)
from nutrition_management.food_knowledge.domain.model import TOP_LEVEL_CATEGORIES
from nutrition_management.food_knowledge.infrastructure.repository import FoodKnowledgeRepository

PACKAGE_FORMAT = "bls-4.0-normalized-v1"
SOURCE_ID = "bls-4.0"
SOURCE_VERSION = "4.0"
SOURCE_DOI = "10.25826/Data20251217-134202-0"
SOURCE_LICENSE = "CC BY 4.0"
PRODUCTION_FOOD_COUNT = 7140
PRODUCTION_COMPONENT_COUNT = 138
_REQUIRED_SOURCE_FILES = frozenset(
    {
        "BLS_4_0_Daten_2025_DE.xlsx",
        "BLS_4_0_Components_DE_EN.xlsx",
    }
)
_REQUIRED_PACKAGE_FILES = frozenset({"components.json", "category_mappings.json"})


@dataclass(frozen=True)
class LoadedBlsV4Package:
    dataset: FoodSourceDataset
    manifest_json: str
    package_digest: str


class BlsV4PackageError(ValueError):
    pass


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def compute_manifest_digest(manifest: dict) -> str:
    payload = dict(manifest)
    payload.pop("package_digest", None)
    return _digest_bytes(canonical_json(payload).encode("utf-8"))


def _json_file(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BlsV4PackageError(f"cannot read valid JSON from {path.name}: {exc}") from exc


def _required_text(value, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise BlsV4PackageError(f"{field} must be a non-empty string")
    return value


def _optional_text(value, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise BlsV4PackageError(f"{field} must be a string or null")
    return value or None


def _sha256_text(value, field: str) -> str:
    digest = _required_text(value, field).lower()
    if len(digest) != 64 or any(char not in string.hexdigits for char in digest):
        raise BlsV4PackageError(f"{field} must be a SHA-256 hex digest")
    return digest


def _decimal(value, field: str) -> Decimal | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise BlsV4PackageError(f"{field} must be a decimal string or null")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise BlsV4PackageError(f"{field} is not a decimal: {value}") from exc
    if not parsed.is_finite():
        raise BlsV4PackageError(f"{field} must be finite")
    return parsed


def _package_filename(value, field: str) -> str:
    name = _required_text(value, field)
    path = PurePosixPath(name)
    if path.is_absolute() or len(path.parts) != 1 or name in {".", ".."}:
        raise BlsV4PackageError(f"{field} must be a package-root filename")
    return name


def _component(row, index: int) -> ComponentDefinition:
    field = f"components.components[{index}]"
    if not isinstance(row, dict):
        raise BlsV4PackageError(f"{field} must be an object")
    try:
        return ComponentDefinition(
            component_code=_required_text(row.get("component_code"), f"{field}.component_code"),
            name_de=_required_text(row.get("name_de"), f"{field}.name_de"),
            name_en=_required_text(row.get("name_en"), f"{field}.name_en"),
            unit=_required_text(row.get("unit"), f"{field}.unit"),
            group_de=_optional_text(row.get("group_de"), f"{field}.group_de"),
            group_en=_optional_text(row.get("group_en"), f"{field}.group_en"),
            formula=_optional_text(row.get("formula"), f"{field}.formula"),
            formula_application=_optional_text(
                row.get("formula_application"), f"{field}.formula_application"
            ),
        )
    except ValueError as exc:
        if isinstance(exc, BlsV4PackageError):
            raise
        raise BlsV4PackageError(f"invalid {field}: {exc}") from exc


def _nutrient(row, food_field: str, index: int) -> SourceNutrientEvidence:
    field = f"{food_field}.nutrients[{index}]"
    if not isinstance(row, dict):
        raise BlsV4PackageError(f"{field} must be an object")
    try:
        return SourceNutrientEvidence(
            component_code=_required_text(row.get("component_code"), f"{field}.component_code"),
            status=NutrientEvidenceStatus(row.get("status")),
            amount_per_100g=_decimal(row.get("amount_per_100g"), f"{field}.amount_per_100g"),
            source_value_text=_required_text(
                row.get("source_value_text"), f"{field}.source_value_text"
            ),
            value_origin=_required_text(row.get("value_origin"), f"{field}.value_origin"),
            source_reference=_optional_text(
                row.get("source_reference"), f"{field}.source_reference"
            ),
        )
    except (ValueError, TypeError) as exc:
        if isinstance(exc, BlsV4PackageError):
            raise
        raise BlsV4PackageError(f"invalid {field}: {exc}") from exc


def _category_mapping(payload) -> dict[str, str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("mappings"), list):
        raise BlsV4PackageError("category_mappings.json requires mappings array")
    result: dict[str, str] = {}
    for index, row in enumerate(payload["mappings"]):
        field = f"category_mappings.mappings[{index}]"
        if not isinstance(row, dict):
            raise BlsV4PackageError(f"{field} must be an object")
        source_code = _required_text(row.get("source_code"), f"{field}.source_code")
        category = _required_text(row.get("category"), f"{field}.category")
        if category not in TOP_LEVEL_CATEGORIES:
            raise BlsV4PackageError(f"{field}.category is not an ADR-005 top-level category")
        if source_code in result:
            raise BlsV4PackageError(f"duplicate category mapping for {source_code}")
        result[source_code] = category
    return result


def _food(row, source_file: str, index: int, category_by_code: dict[str, str]) -> SourceFood:
    field = f"{source_file}.foods[{index}]"
    if not isinstance(row, dict):
        raise BlsV4PackageError(f"{field} must be an object")
    source_code = _required_text(row.get("source_code"), f"{field}.source_code")
    if source_code not in category_by_code:
        raise BlsV4PackageError(f"{field}.source_code has no explicit category mapping: {source_code}")
    nutrients = row.get("nutrients")
    if not isinstance(nutrients, list):
        raise BlsV4PackageError(f"{field}.nutrients must be an array")
    try:
        return SourceFood(
            base_food_id=f"{SOURCE_ID}:{source_code}",
            source_code=source_code,
            name_de=_required_text(row.get("name_de"), f"{field}.name_de"),
            name_en=_optional_text(row.get("name_en"), f"{field}.name_en"),
            category=category_by_code[source_code],
            nutrients=tuple(_nutrient(item, field, item_index) for item_index, item in enumerate(nutrients)),
        )
    except ValueError as exc:
        if isinstance(exc, BlsV4PackageError):
            raise
        raise BlsV4PackageError(f"invalid {field}: {exc}") from exc


def load_bls_v4_package(
    directory: Path,
    *,
    expected_food_count: int = PRODUCTION_FOOD_COUNT,
    expected_component_count: int = PRODUCTION_COMPONENT_COUNT,
) -> LoadedBlsV4Package:
    manifest = _json_file(directory / "manifest.json")
    if not isinstance(manifest, dict):
        raise BlsV4PackageError("manifest must be an object")
    if manifest.get("package_format") != PACKAGE_FORMAT:
        raise BlsV4PackageError(f"manifest.package_format must be {PACKAGE_FORMAT}")

    source = manifest.get("source")
    if not isinstance(source, dict):
        raise BlsV4PackageError("manifest.source must be an object")
    source_id = _required_text(source.get("id"), "manifest.source.id")
    source_version = _required_text(source.get("version"), "manifest.source.version")
    doi = _required_text(source.get("doi"), "manifest.source.doi")
    license_name = _required_text(source.get("license"), "manifest.source.license")
    if source_id != SOURCE_ID or source_version != SOURCE_VERSION:
        raise BlsV4PackageError("normalized package must identify BLS source bls-4.0 / version 4.0")
    if doi != SOURCE_DOI or license_name != SOURCE_LICENSE:
        raise BlsV4PackageError("normalized package BLS DOI/license does not match the pinned source")

    source_files = manifest.get("source_files")
    if not isinstance(source_files, dict) or not _REQUIRED_SOURCE_FILES.issubset(source_files):
        raise BlsV4PackageError(
            f"manifest.source_files must contain at least {sorted(_REQUIRED_SOURCE_FILES)}"
        )
    normalized_source_files: dict[str, str] = {}
    for raw_name, raw_digest in source_files.items():
        name = _package_filename(raw_name, "manifest.source_files key")
        normalized_source_files[name] = _sha256_text(
            raw_digest, f"manifest.source_files.{name}"
        )
    source_digest = _digest_bytes(canonical_json(normalized_source_files).encode("utf-8"))

    files = manifest.get("files")
    if not isinstance(files, dict) or not _REQUIRED_PACKAGE_FILES.issubset(files):
        raise BlsV4PackageError(
            f"manifest.files must contain at least {sorted(_REQUIRED_PACKAGE_FILES)}"
        )
    food_files_raw = manifest.get("food_files")
    if not isinstance(food_files_raw, list) or not food_files_raw:
        raise BlsV4PackageError("manifest.food_files must be a non-empty array")
    food_files = tuple(
        _package_filename(name, "manifest.food_files") for name in food_files_raw
    )
    if len(food_files) != len(set(food_files)):
        raise BlsV4PackageError("manifest.food_files must be unique")
    for name in food_files:
        if not (name.startswith("foods.") and name.endswith(".json")):
            raise BlsV4PackageError(f"invalid food shard filename {name}")
        if name not in files:
            raise BlsV4PackageError(f"food shard {name} is missing from manifest.files")

    for raw_name, raw_digest in files.items():
        name = _package_filename(raw_name, "manifest.files key")
        expected_digest = _sha256_text(raw_digest, f"manifest.files.{name}")
        try:
            actual_digest = _digest_bytes((directory / name).read_bytes())
        except OSError as exc:
            raise BlsV4PackageError(f"cannot read package file {name}: {exc}") from exc
        if expected_digest != actual_digest:
            raise BlsV4PackageError(f"digest mismatch for {name}")

    package_digest = _required_text(manifest.get("package_digest"), "manifest.package_digest")
    if package_digest != compute_manifest_digest(manifest):
        raise BlsV4PackageError("manifest package_digest does not match canonical manifest content")

    manifest_food_count = manifest.get("food_count")
    manifest_component_count = manifest.get("component_count")
    if manifest_food_count != expected_food_count:
        raise BlsV4PackageError(
            f"manifest.food_count must be {expected_food_count}, got {manifest_food_count}"
        )
    if manifest_component_count != expected_component_count:
        raise BlsV4PackageError(
            f"manifest.component_count must be {expected_component_count}, got {manifest_component_count}"
        )

    components_payload = _json_file(directory / "components.json")
    if not isinstance(components_payload, dict) or not isinstance(
        components_payload.get("components"), list
    ):
        raise BlsV4PackageError("components.json requires components array")
    components = tuple(
        _component(row, index) for index, row in enumerate(components_payload["components"])
    )
    if len(components) != expected_component_count:
        raise BlsV4PackageError(
            f"expected {expected_component_count} component definitions, got {len(components)}"
        )

    category_by_code = _category_mapping(_json_file(directory / "category_mappings.json"))
    foods: list[SourceFood] = []
    for food_file in food_files:
        payload = _json_file(directory / food_file)
        if not isinstance(payload, dict) or not isinstance(payload.get("foods"), list):
            raise BlsV4PackageError(f"{food_file} requires foods array")
        foods.extend(
            _food(row, food_file, index, category_by_code)
            for index, row in enumerate(payload["foods"])
        )
    if len(foods) != expected_food_count:
        raise BlsV4PackageError(f"expected {expected_food_count} foods, got {len(foods)}")

    food_codes = [item.source_code for item in foods]
    if len(food_codes) != len(set(food_codes)):
        raise BlsV4PackageError("BLS source food codes must be unique across all shards")
    if set(category_by_code) != set(food_codes):
        missing = sorted(set(food_codes) - set(category_by_code))
        extra = sorted(set(category_by_code) - set(food_codes))
        raise BlsV4PackageError(
            f"category registry must cover source foods exactly; missing={missing}, extra={extra}"
        )

    try:
        dataset = FoodSourceDataset(
            source_id=source_id,
            source_name=_required_text(source.get("name"), "manifest.source.name"),
            source_version=source_version,
            source_digest=source_digest,
            package_digest=package_digest,
            doi=doi,
            license=license_name,
            source_url=_required_text(source.get("url"), "manifest.source.url"),
            attribution=_required_text(source.get("attribution"), "manifest.source.attribution"),
            components=components,
            foods=tuple(foods),
        )
    except ValueError as exc:
        raise BlsV4PackageError(f"invalid normalized BLS dataset: {exc}") from exc

    return LoadedBlsV4Package(
        dataset=dataset,
        manifest_json=canonical_json(manifest),
        package_digest=package_digest,
    )


def import_bls_v4_package(
    repository: FoodKnowledgeRepository,
    package: LoadedBlsV4Package,
) -> str:
    dataset = package.dataset
    existing = repository.source_dataset_digests(dataset.source_id)
    if existing is not None:
        existing_source_digest, existing_package_digest = existing
        if (
            existing_source_digest != dataset.source_digest
            or existing_package_digest != dataset.package_digest
        ):
            raise BlsV4PackageError(
                f"immutable Food Knowledge source {dataset.source_id} already exists with different content"
            )
        return "unchanged"

    repository.add_source_dataset(dataset, manifest_json=package.manifest_json)
    return "inserted"
