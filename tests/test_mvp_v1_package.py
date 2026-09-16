from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from nutrition_management.nutrition_targeting.application.service import derive_household_target_fact
from nutrition_management.nutrition_targeting.domain.model import NutritionProfile, Sex
from nutrition_management.nutrition_targeting.infrastructure.mvp_v1_standard_data import load_mvp_v1_standard_package
from nutrition_management.nutrition_targeting.infrastructure.repository import NutritionTargetingRepository
from nutrition_management.nutrition_targeting.infrastructure.standard_data import import_standard_package


_DATA = Path(__file__).resolve().parents[1] / "data" / "nutrition" / "mvp-v1"
_DERIVATION_DATE = date(2026, 9, 16)


def _profile(member_id: str, sex: Sex, *, height: str, weight: str) -> NutritionProfile:
    return NutritionProfile(
        member_id=member_id,
        date_of_birth=date(1990, 6, 15),
        sex=sex,
        height_m=Decimal(height),
        current_weight_kg=Decimal(weight),
        current_weight_date=date(2026, 9, 15),
        pal=Decimal("1.6"),
    )


def test_committed_mvp_v1_package_imports_idempotently_and_derives_adult_coverage(engine):
    package = load_mvp_v1_standard_package(_DATA)
    assert package.standard.version == "mvp-v1"
    assert package.standard.content_digest == package.package_digest
    assert package.standard.safety_mappings

    with engine.begin() as connection:
        repository = NutritionTargetingRepository(connection)
        assert import_standard_package(repository, package, active=True) == "inserted"
        assert import_standard_package(repository, package, active=True) == "unchanged"
        repository.add_profile("household", _profile("male", Sex.MALE, height="1.80", weight="75"))
        repository.add_profile("household", _profile("female", Sex.FEMALE, height="1.68", weight="62"))

    with engine.connect() as connection:
        repository = NutritionTargetingRepository(connection)
        persisted = repository.active_standard()
        assert persisted.version == "mvp-v1"
        assert persisted.content_digest == package.package_digest
        assert persisted.safety_mappings == package.standard.safety_mappings
        target = derive_household_target_fact(repository, "household", _DERIVATION_DATE)

    resolved_measures = {item.measure for item in target.targets}
    assert {"PROT625", "FIBT"} <= resolved_measures

    target_gaps = {(gap.member_id, gap.family_id, gap.state) for gap in target.target_coverage_gaps}
    assert ("male", "dge.zinc", "unsupported_applicability") in target_gaps
    assert ("female", "dge.zinc", "unsupported_applicability") in target_gaps
    assert ("female", "dge.iron", "unsupported_applicability") in target_gaps
    assert ("male", "dge.iodine", "unsupported_mapping") in target_gaps
    assert ("male", "dge.selenium", "unsupported_mapping") in target_gaps
    assert ("male", "dge.water_total", "unsupported_mapping") in target_gaps
    assert ("male", "dge.carbohydrates", "unsupported_target_shape") in target_gaps
    assert ("male", "dge.mufa", "unsupported_target_shape") in target_gaps

    safety_measures = {item.measure for item in target.member_safety_limits}
    assert {"CA", "CU", "ZN", "FE", "VITB6", "VITE"} <= safety_measures

    safety_gaps = {(gap.member_id, gap.family_id, gap.state) for gap in target.safety_coverage_gaps}
    assert ("male", "efsa.magnesium.dissociable", "unsupported_mapping") in safety_gaps
    assert ("male", "efsa.folate.added_forms", "unsupported_mapping") in safety_gaps
    assert ("male", "efsa.nicotinamide", "unsupported_mapping") in safety_gaps
    assert ("male", "efsa.vitamin_a.preformed", "unsupported_mapping") in safety_gaps
    assert ("male", "efsa.vitamin_d.vde", "unsupported_mapping") in safety_gaps
