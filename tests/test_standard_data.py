from __future__ import annotations

from datetime import date
from decimal import Decimal
from hashlib import sha256
import json

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import inspect

from nutrition_management.composition.database import create_sqlite_engine
from nutrition_management.nutrition_targeting.domain.model import (
    AgeBoundary,
    AgeUnit,
    ApplicableWeightRule,
    ApplicabilityRequirement,
    MappingStatus,
    NutritionProfile,
    NutritionStandardSet,
    ReferenceApplicability,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceGapState,
    ReferenceKind,
    Sex,
    SourceSemanticKind,
    TargetMapping,
    completed_calendar_months,
)
from nutrition_management.nutrition_targeting.domain.targets import derive_member_target
from nutrition_management.nutrition_targeting.infrastructure.repository import NutritionTargetingRepository
from nutrition_management.nutrition_targeting.infrastructure.standard_data import (
    StandardPackageError,
    compute_manifest_digest,
    import_standard_package,
    load_standard_package,
)


def _profile(weight: str = "70", height: str = "1.70") -> NutritionProfile:
    return NutritionProfile(
        member_id="member",
        date_of_birth=date(1990, 1, 31),
        sex=Sex.FEMALE,
        height_m=Decimal(height),
        current_weight_kg=Decimal(weight),
        current_weight_date=date(2026, 9, 14),
        pal=Decimal("1.6"),
    )


def _mapping(family_id: str, measure: str, unit: str) -> TargetMapping:
    return TargetMapping(family_id, MappingStatus.MAPPED, measure, unit)


def test_completed_calendar_months_clamps_monthly_anniversary_to_month_end():
    assert completed_calendar_months(date(2026, 1, 31), date(2026, 2, 27)) == 0
    assert completed_calendar_months(date(2026, 1, 31), date(2026, 2, 28)) == 1
    assert completed_calendar_months(date(2024, 2, 29), date(2025, 2, 28)) == 12


def test_adult_zinc_with_unowned_phytate_class_is_unsupported_applicability():
    rows = tuple(
        ReferenceDefinition(
            reference_id=f"zinc-{level}",
            family_id="zinc-adult-female",
            nutrient_measure="zinc",
            kind=ReferenceKind.ADEQUACY_FLOOR,
            basis=ReferenceBasis.ABSOLUTE_DAILY,
            lower=value,
            source_semantic_kind=SourceSemanticKind.RECOMMENDED_INTAKE,
            source_unit="mg",
            applicability=ReferenceApplicability(
                min_age=AgeBoundary(19, AgeUnit.YEARS),
                sex=Sex.FEMALE,
                requirements=(ApplicabilityRequirement("phytate_class", level),),
            ),
        )
        for level, value in (("low", Decimal(7)), ("medium", Decimal(8)), ("high", Decimal(10)))
    )
    standard = NutritionStandardSet(
        "zinc-test",
        rows,
        mappings=(_mapping("zinc-adult-female", "ZN", "mg"),),
    )

    target = derive_member_target(_profile(), standard, date(2026, 9, 15))
    assert target.references == ()
    assert len(target.reference_gaps) == 1
    gap = target.reference_gaps[0]
    assert gap.state == ReferenceGapState.UNSUPPORTED_APPLICABILITY
    assert gap.missing_dimensions == ("phytate_class",)
    assert set(gap.candidate_reference_ids) == {"zinc-low", "zinc-medium", "zinc-high"}


def _protein_standard() -> NutritionStandardSet:
    return NutritionStandardSet(
        "protein-test",
        (
            ReferenceDefinition(
                reference_id="protein-adult",
                family_id="protein-adult",
                nutrient_measure="protein",
                kind=ReferenceKind.ADEQUACY_FLOOR,
                basis=ReferenceBasis.PER_KG_DAILY,
                lower=Decimal(1),
                source_semantic_kind=SourceSemanticKind.RECOMMENDED_INTAKE,
                source_unit="g",
                applicable_weight_rule=ApplicableWeightRule.DGE_ADULT_PROTEIN,
                applicability=ReferenceApplicability(min_age=AgeBoundary(19, AgeUnit.YEARS)),
            ),
        ),
        mappings=(_mapping("protein-adult", "PROT625", "g"),),
    )


def test_adult_protein_weight_rule_uses_current_weight_then_bmi22_and_stops_at_obesity():
    standard = _protein_standard()

    normal = derive_member_target(_profile(weight="74", height="2"), standard, date(2026, 9, 15))
    assert normal.references[0].lower_30d == Decimal(74) * 30

    overweight = derive_member_target(_profile(weight="100", height="2"), standard, date(2026, 9, 15))
    assert overweight.references[0].lower_30d == Decimal(88) * 30

    obese = derive_member_target(_profile(weight="120", height="2"), standard, date(2026, 9, 15))
    assert obese.references == ()
    assert obese.reference_gaps[0].state == ReferenceGapState.SOURCE_INAPPLICABLE

    underweight = derive_member_target(_profile(weight="73.99", height="2"), standard, date(2026, 9, 15))
    assert underweight.references == ()
    assert underweight.reference_gaps[0].state == ReferenceGapState.SOURCE_INAPPLICABLE


def test_per_1000_kcal_reference_and_exact_mass_unit_scaling():
    standard = NutritionStandardSet(
        "density-test",
        (
            ReferenceDefinition(
                reference_id="density-row",
                family_id="density",
                nutrient_measure="source-density",
                kind=ReferenceKind.ADEQUACY_FLOOR,
                basis=ReferenceBasis.PER_1000_KCAL,
                lower=Decimal(2),
                source_semantic_kind=SourceSemanticKind.GUIDELINE,
                source_unit="mg",
            ),
        ),
        mappings=(_mapping("density", "VITB6", "µg"),),
    )
    target = derive_member_target(_profile(), standard, date(2026, 9, 15))
    assert target.references[0].lower_30d == target.energy_kcal_30d * Decimal(2)


def _canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_package(directory, *, lower="10"):
    references = {
        "rows": [
            {
                "family_id": "vitamin-c-adult",
                "row_id": "vitamin-c-adult-female",
                "nutrient_measure": "vitamin_c",
                "source_semantic_kind": "recommended_intake",
                "target_kind": "adequacy_floor",
                "basis": "absolute_daily",
                "source_unit": "mg",
                "lower": lower,
                "upper": None,
                "point": None,
                "energy_kcal_per_g": None,
                "scope": "active",
                "applicability": {"min_age": {"value": 19, "unit": "years"}, "sex": "female"},
                "source_id": "source",
                "source_locator": "table-row",
            }
        ]
    }
    safety = {"rows": []}
    mappings = {
        "mappings": [
            {
                "family_id": "vitamin-c-adult",
                "status": "mapped",
                "nutrient_measure": "VITC",
                "canonical_unit": "mg",
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
        "standard_version": "test-package-v1",
        "sources": [{"id": "source", "name": "test", "version": "1", "url": "https://example.invalid/source"}],
        "files": {name: sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    manifest["package_digest"] = compute_manifest_digest(manifest)
    (directory / "manifest.json").write_bytes(_canonical_bytes(manifest))


def test_standard_package_round_trips_and_reimport_is_idempotent(engine, tmp_path):
    package_dir = tmp_path / "package"
    package_dir.mkdir()
    _write_package(package_dir)
    package = load_standard_package(package_dir)

    with engine.begin() as connection:
        repo = NutritionTargetingRepository(connection)
        assert import_standard_package(repo, package, active=True) == "inserted"
        assert import_standard_package(repo, package, active=True) == "unchanged"

    with engine.connect() as connection:
        loaded = NutritionTargetingRepository(connection).active_standard()
    assert loaded.version == "test-package-v1"
    assert loaded.content_digest == package.package_digest
    assert loaded.references[0].family_id == "vitamin-c-adult"
    assert loaded.references[0].source_semantic_kind == SourceSemanticKind.RECOMMENDED_INTAKE
    assert loaded.mappings[0].nutrient_measure == "VITC"


def test_same_standard_version_with_different_package_digest_is_rejected(engine, tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    _write_package(first_dir, lower="10")
    _write_package(second_dir, lower="11")
    first = load_standard_package(first_dir)
    second = load_standard_package(second_dir)

    with engine.begin() as connection:
        repo = NutritionTargetingRepository(connection)
        import_standard_package(repo, first, active=False)
        with pytest.raises(StandardPackageError, match="different content"):
            import_standard_package(repo, second, active=False)


def test_migration_from_0001_adds_production_standard_tables_and_columns(tmp_path):
    db_path = tmp_path / "migration.db"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "0001")
    command.upgrade(config, "head")

    engine = create_sqlite_engine(db_path)
    try:
        inspector = inspect(engine)
        assert "nt_reference_mapping" in inspector.get_table_names()
        standard_columns = {item["name"] for item in inspector.get_columns("nt_standard_set")}
        reference_columns = {item["name"] for item in inspector.get_columns("nt_standard_reference")}
        assert {"content_digest", "source_manifest"} <= standard_columns
        assert {"family_id", "source_semantic_kind", "applicability_json", "source_locator"} <= reference_columns
    finally:
        engine.dispose()
