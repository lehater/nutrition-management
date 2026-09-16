from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import string

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.application.source_data import FoodSourceDataset

BLS_VALUE_ORIGINS = frozenset(
    {
        "Analyse",
        "Rezeptberechnung",
        "Musterberechnung",
        "Aggregation",
        "Literatur",
        "Labelangabe",
        "Nährstoffdatenbank",
        "Übernommener Wert",
        "Reskalierung",
        "Logische Null",
        "Logische Annahme",
        "Spuren",
        "Formelberechnung",
    }
)
CURRENT_ERRATA_STATE = "2026-08"
_REQUIRED_GOVERNANCE_FILES = frozenset({"corrections.json", "errata_coverage.json"})
_CORRECTION_TYPES = frozenset(
    {
        "direct_value",
        "source_metadata",
        "formula_recalculation",
        "recipe_propagation",
    }
)
_COVERAGE_OUTCOMES = frozenset({"applied_directly", "recomputed", "non_applicable"})


class BlsV4SemanticError(ValueError):
    pass


def _required_text(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BlsV4SemanticError(f"{field} must be a non-empty string")
    return value.strip()


def _sha256(value, field: str) -> str:
    digest = _required_text(value, field).lower()
    if len(digest) != 64 or any(char not in string.hexdigits for char in digest):
        raise BlsV4SemanticError(f"{field} must be a SHA-256 hex digest")
    return digest


def _json_file(path: Path, field: str):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BlsV4SemanticError(f"cannot read valid JSON for {field}: {exc}") from exc


def normalize_bls_value(
    source_value_text: str | None,
    value_origin: str | None,
) -> tuple[NutrientEvidenceStatus, Decimal | None]:
    """Interpret one BLS value/origin pair before any quantitative planning use."""

    text = "" if source_value_text is None else source_value_text.strip()
    origin = "" if value_origin is None else value_origin.strip()

    if text in {"", "-"}:
        if origin not in {"", "-"}:
            raise BlsV4SemanticError("missing BLS value must not carry a non-empty origin")
        return NutrientEvidenceStatus.MISSING, None

    if origin not in BLS_VALUE_ORIGINS:
        raise BlsV4SemanticError(f"unsupported BLS data origin: {origin or '<empty>'}")

    if text == "TR":
        if origin != "Spuren":
            raise BlsV4SemanticError("BLS TR evidence must use data origin Spuren")
        return NutrientEvidenceStatus.TRACE, None
    if origin == "Spuren":
        raise BlsV4SemanticError("BLS data origin Spuren must use the TR value marker")

    if text == "<LOQ":
        return NutrientEvidenceStatus.BELOW_QUANTIFICATION_LIMIT, None
    if text == "<LOD":
        return NutrientEvidenceStatus.BELOW_DETECTION_LIMIT, None

    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise BlsV4SemanticError(f"unsupported BLS value marker: {text}") from exc
    if not amount.is_finite() or amount < 0:
        raise BlsV4SemanticError("BLS numeric nutrient value must be finite and non-negative")
    if origin == "Logische Null" and amount != 0:
        raise BlsV4SemanticError("BLS Logische Null must contain numeric zero")
    return (
        NutrientEvidenceStatus.ZERO if amount == 0 else NutrientEvidenceStatus.KNOWN,
        amount,
    )


def validate_dataset_evidence(dataset: FoodSourceDataset) -> None:
    for food in dataset.foods:
        for evidence in food.nutrients:
            expected_status, expected_amount = normalize_bls_value(
                evidence.source_value_text,
                evidence.value_origin,
            )
            if evidence.status != expected_status or evidence.amount_per_100g != expected_amount:
                raise BlsV4SemanticError(
                    "normalized BLS evidence disagrees with raw value/origin semantics: "
                    f"food={food.source_code}, component={evidence.component_code}, "
                    f"expected=({expected_status.value},{expected_amount}), "
                    f"actual=({evidence.status.value},{evidence.amount_per_100g})"
                )


def validate_errata_contract(directory: Path, manifest: dict) -> None:
    errata = manifest.get("errata")
    if not isinstance(errata, dict):
        raise BlsV4SemanticError("manifest.errata must be an object")
    if _required_text(errata.get("state"), "manifest.errata.state") != CURRENT_ERRATA_STATE:
        raise BlsV4SemanticError(
            f"manifest.errata.state must pin current accepted BLS errata {CURRENT_ERRATA_STATE}"
        )
    _required_text(errata.get("locator"), "manifest.errata.locator")
    _sha256(errata.get("sha256"), "manifest.errata.sha256")
    if errata.get("coverage_complete") is not True:
        raise BlsV4SemanticError("manifest.errata.coverage_complete must be true")

    files = manifest.get("files")
    if not isinstance(files, dict) or not _REQUIRED_GOVERNANCE_FILES.issubset(files):
        raise BlsV4SemanticError(
            f"manifest.files must contain BLS errata governance files {sorted(_REQUIRED_GOVERNANCE_FILES)}"
        )

    corrections_payload = _json_file(directory / "corrections.json", "corrections.json")
    coverage_payload = _json_file(directory / "errata_coverage.json", "errata_coverage.json")
    if not isinstance(corrections_payload, dict) or not isinstance(
        corrections_payload.get("corrections"), list
    ):
        raise BlsV4SemanticError("corrections.json requires corrections array")
    if not isinstance(coverage_payload, dict) or not isinstance(coverage_payload.get("entries"), list):
        raise BlsV4SemanticError("errata_coverage.json requires entries array")

    correction_ids: set[str] = set()
    for index, row in enumerate(corrections_payload["corrections"]):
        field = f"corrections.corrections[{index}]"
        if not isinstance(row, dict):
            raise BlsV4SemanticError(f"{field} must be an object")
        correction_id = _required_text(row.get("id"), f"{field}.id")
        if correction_id in correction_ids:
            raise BlsV4SemanticError(f"duplicate correction id {correction_id}")
        correction_type = _required_text(row.get("type"), f"{field}.type")
        if correction_type not in _CORRECTION_TYPES:
            raise BlsV4SemanticError(f"unsupported BLS correction type: {correction_type}")
        if not isinstance(row.get("scope"), dict) or not row["scope"]:
            raise BlsV4SemanticError(f"{field}.scope must be a non-empty object")
        _required_text(row.get("source_locator"), f"{field}.source_locator")
        correction_ids.add(correction_id)

    coverage_ids: set[str] = set()
    for index, row in enumerate(coverage_payload["entries"]):
        field = f"errata_coverage.entries[{index}]"
        if not isinstance(row, dict):
            raise BlsV4SemanticError(f"{field} must be an object")
        correction_id = _required_text(row.get("correction_id"), f"{field}.correction_id")
        if correction_id in coverage_ids:
            raise BlsV4SemanticError(f"duplicate errata coverage for {correction_id}")
        outcome = _required_text(row.get("outcome"), f"{field}.outcome")
        if outcome not in _COVERAGE_OUTCOMES:
            raise BlsV4SemanticError(f"unsupported errata coverage outcome: {outcome}")
        if outcome == "non_applicable":
            _required_text(row.get("reason"), f"{field}.reason")
        coverage_ids.add(correction_id)

    if coverage_ids != correction_ids:
        missing = sorted(correction_ids - coverage_ids)
        extra = sorted(coverage_ids - correction_ids)
        raise BlsV4SemanticError(
            f"errata coverage must account for corrections exactly; missing={missing}, extra={extra}"
        )
