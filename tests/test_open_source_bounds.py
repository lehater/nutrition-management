from __future__ import annotations

from datetime import date
from hashlib import sha256
import json

from nutrition_management.nutrition_targeting.domain.model import NutritionProfile, ReferenceGapState, Sex
from nutrition_management.nutrition_targeting.domain.targets import derive_member_target
from nutrition_management.nutrition_targeting.infrastructure.repository import NutritionTargetingRepository
from nutrition_management.nutrition_targeting.infrastructure.standard_data import (
    compute_manifest_digest,
    import_standard_package,
    load_standard_package,
)


def _canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def test_open_source_bound_round_trips_and_stays_out_of_numeric_target(engine, tmp_path):
    directory = tmp_path / "open-bound"
    directory.mkdir()
    references = {
        "rows": [
            {
                "family_id": "carbohydrate-guideline",
                "row_id": "carbohydrate-guideline-adult",
                "nutrient_measure": "carbohydrate",
                "source_semantic_kind": "guideline",
                "target_kind": "lower_bound",
                "basis": "percent_energy",
                "source_unit": "percent_energy",
                "lower": "50",
                "lower_inclusive": False,
                "upper": None,
                "point": None,
                "energy_kcal_per_g": "4",
                "scope": "active",
                "applicability": {"min_age": {"value": 19, "unit": "years"}},
                "source_id": "source",
                "source_locator": "more-than-50-percent-energy",
            }
        ]
    }
    safety = {"rows": []}
    mappings = {
        "mappings": [
            {
                "family_id": "carbohydrate-guideline",
                "status": "mapped",
                "nutrient_measure": "CHO",
                "canonical_unit": "g",
                "formula_id": None,
                "reason": None,
            }
        ]
    }
    payloads = {
        "references.json": _canonical_bytes(references),
        "safety_limits.json": _canonical_bytes(safety),
        "mappings.json": _canonical_bytes(mappings),
    }
    for name, payload in payloads.items():
        (directory / name).write_bytes(payload)
    manifest = {
        "standard_version": "open-bound-test-v1",
        "sources": [{"id": "source", "name": "test", "version": "1", "url": "https://example.invalid/source"}],
        "files": {name: sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    manifest["package_digest"] = compute_manifest_digest(manifest)
    (directory / "manifest.json").write_bytes(_canonical_bytes(manifest))

    package = load_standard_package(directory)
    assert package.standard.references[0].lower_inclusive is False

    with engine.begin() as connection:
        repo = NutritionTargetingRepository(connection)
        import_standard_package(repo, package, active=True)
    with engine.connect() as connection:
        standard = NutritionTargetingRepository(connection).active_standard()
    assert standard.references[0].lower_inclusive is False

    profile = NutritionProfile(
        member_id="adult",
        date_of_birth=date(1990, 1, 1),
        sex=Sex.MALE,
        height_m=1.8,
        current_weight_kg=75,
        current_weight_date=date(2026, 9, 16),
        pal=1.6,
    )
    target = derive_member_target(profile, standard, date(2026, 9, 16))
    assert target.references == ()
    assert target.reference_gaps[0].state == ReferenceGapState.UNSUPPORTED_TARGET_SHAPE
