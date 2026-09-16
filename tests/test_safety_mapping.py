from datetime import date
from decimal import Decimal

from nutrition_management.nutrition_targeting.domain.model import (
    MappingStatus,
    NutritionProfile,
    NutritionStandardSet,
    ReferenceApplicability,
    SafetyDefinition,
    SafetyGapState,
    SafetyMapping,
    Sex,
)
from nutrition_management.nutrition_targeting.domain.targets import derive_member_target


def _profile() -> NutritionProfile:
    return NutritionProfile(
        member_id="adult",
        date_of_birth=date(1990, 1, 1),
        sex=Sex.MALE,
        height_m=Decimal("1.80"),
        current_weight_kg=Decimal("75"),
        current_weight_date=date(2026, 9, 16),
        pal=Decimal("1.6"),
    )


def test_only_explicitly_mapped_safety_limits_become_numeric_diagnostics():
    exact = SafetyDefinition(
        reference_id="safety-zinc-adult",
        family_id="safety-zinc",
        nutrient_measure="zinc-total",
        daily_upper=Decimal("0.025"),
        source_unit="g",
        substance_scope="total zinc from all dietary sources",
        applicability=ReferenceApplicability(),
    )
    narrow = SafetyDefinition(
        reference_id="safety-niacin-nicotinic-acid",
        family_id="safety-nicotinic-acid",
        nutrient_measure="nicotinic-acid",
        daily_upper=Decimal("10"),
        source_unit="mg",
        substance_scope="nicotinic acid only",
        applicability=ReferenceApplicability(),
    )
    standard = NutritionStandardSet(
        version="safety-mapping-test",
        references=(),
        safety_limits=(exact, narrow),
        safety_mappings=(
            SafetyMapping("safety-zinc", MappingStatus.MAPPED, "ZN", "mg"),
            SafetyMapping(
                "safety-nicotinic-acid",
                MappingStatus.UNSUPPORTED,
                reason="aggregate niacin equivalents are broader than nicotinic acid",
            ),
        ),
    )

    target = derive_member_target(_profile(), standard, date(2026, 9, 16))

    assert len(target.safety_limits) == 1
    assert target.safety_limits[0].nutrient_measure == "ZN"
    assert target.safety_limits[0].daily_upper == Decimal("25")
    assert len(target.safety_gaps) == 1
    assert target.safety_gaps[0].family_id == "safety-nicotinic-acid"
    assert target.safety_gaps[0].state == SafetyGapState.UNSUPPORTED_MAPPING
