from datetime import date
from decimal import Decimal

import pytest

from nutrition_management.nutrition_targeting.domain.aggregation import aggregate_household_target
from nutrition_management.nutrition_targeting.domain.energy import adult_maintenance_energy_kcal_per_day
from nutrition_management.nutrition_targeting.domain.model import (
    NutritionProfile,
    NutritionStandardSet,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceKind,
    Sex,
    UnsupportedSliceCapability,
    chronological_age_years,
)
from nutrition_management.nutrition_targeting.domain.targets import derive_member_target


def profile(member_id: str = "m1", *, sex: Sex = Sex.FEMALE) -> NutritionProfile:
    return NutritionProfile(
        member_id=member_id,
        date_of_birth=date(1990, 9, 16),
        sex=sex,
        height_m=Decimal("1.70"),
        current_weight_kg=Decimal("70"),
        current_weight_date=date(2026, 9, 14),
        pal=Decimal("1.6"),
    )


def standard() -> NutritionStandardSet:
    return NutritionStandardSet(
        version="test-slice-v1",
        references=(
            ReferenceDefinition(
                reference_id="protein",
                nutrient_measure="PROT625",
                kind=ReferenceKind.ADEQUACY_FLOOR,
                basis=ReferenceBasis.PER_KG_DAILY,
                lower=Decimal("0.8"),
            ),
            ReferenceDefinition(
                reference_id="fiber",
                nutrient_measure="FIBT",
                kind=ReferenceKind.ADEQUACY_FLOOR,
                basis=ReferenceBasis.ABSOLUTE_DAILY,
                lower=Decimal("30"),
            ),
            ReferenceDefinition(
                reference_id="carb-share",
                nutrient_measure="CHO",
                kind=ReferenceKind.INTERVAL,
                basis=ReferenceBasis.PERCENT_ENERGY,
                lower=Decimal("0.45"),
                upper=Decimal("0.55"),
                energy_kcal_per_g=Decimal("4"),
            ),
        ),
    )


def test_age_changes_exactly_on_birthday():
    dob = date(2000, 9, 16)
    assert chronological_age_years(dob, date(2026, 9, 15)) == 25
    assert chronological_age_years(dob, date(2026, 9, 16)) == 26


def test_adult_energy_uses_sex_specific_dge_formula():
    as_of = date(2026, 9, 15)
    female = adult_maintenance_energy_kcal_per_day(profile(sex=Sex.FEMALE), as_of)
    male = adult_maintenance_energy_kcal_per_day(profile(sex=Sex.MALE), as_of)
    assert female > 0
    assert male > female


def test_future_weight_observation_is_rejected():
    bad = profile()
    bad = NutritionProfile(**{**bad.__dict__, "current_weight_date": date(2026, 9, 16)})
    with pytest.raises(ValueError, match="current_weight_date"):
        adult_maintenance_energy_kcal_per_day(bad, date(2026, 9, 15))


def test_pal_above_unadjusted_range_requires_activity_adjustment_provenance():
    base = profile()
    unproven = NutritionProfile(**{**base.__dict__, "pal": Decimal("2.5")})
    with pytest.raises(ValueError, match="unadjusted PAL"):
        adult_maintenance_energy_kcal_per_day(unproven, date(2026, 9, 15))

    adjusted = NutritionProfile(
        **{
            **base.__dict__,
            "pal": Decimal("2.5"),
            "pal_activity_adjustment_applied": True,
        }
    )
    assert adult_maintenance_energy_kcal_per_day(adjusted, date(2026, 9, 15)) > 0
    target = derive_member_target(adjusted, standard(), date(2026, 9, 15))
    assert target.pal == Decimal("2.5")
    assert target.pal_activity_adjustment_applied is True


def test_adjustment_flag_requires_adjusted_pal_range():
    base = profile()
    invalid = NutritionProfile(
        **{
            **base.__dict__,
            "pal": Decimal("1.4"),
            "pal_activity_adjustment_applied": True,
        }
    )
    with pytest.raises(ValueError, match="activity-adjusted PAL"):
        adult_maintenance_energy_kcal_per_day(invalid, date(2026, 9, 15))


def test_active_weight_goal_fails_explicitly_in_slice():
    base = profile()
    active = NutritionProfile(
        **{
            **base.__dict__,
            "target_weight_kg": Decimal("65"),
            "target_date": date(2027, 1, 1),
        }
    )
    with pytest.raises(UnsupportedSliceCapability):
        adult_maintenance_energy_kcal_per_day(active, date(2026, 9, 15))


def test_active_weight_goal_with_nonfuture_target_date_is_invalid():
    base = profile()
    invalid = NutritionProfile(
        **{
            **base.__dict__,
            "target_weight_kg": Decimal("65"),
            "target_date": date(2026, 9, 15),
        }
    )
    with pytest.raises(ValueError, match="target_date"):
        adult_maintenance_energy_kcal_per_day(invalid, date(2026, 9, 15))


def test_profile_rejects_nonpositive_body_measurements():
    base = profile()
    with pytest.raises(ValueError, match="current weight"):
        NutritionProfile(**{**base.__dict__, "current_weight_kg": Decimal("0")})
    with pytest.raises(ValueError, match="height"):
        NutritionProfile(**{**base.__dict__, "height_m": Decimal("0")})


def test_reference_resolution_preserves_kind_and_scales_to_30_days():
    target = derive_member_target(profile(), standard(), date(2026, 9, 15))
    protein = next(item for item in target.references if item.nutrient_measure == "PROT625")
    fiber = next(item for item in target.references if item.nutrient_measure == "FIBT")
    assert protein.kind == ReferenceKind.ADEQUACY_FLOOR
    assert protein.lower_30d == Decimal("1680")
    assert fiber.lower_30d == Decimal("900")
    assert target.current_weight_kg == Decimal("70")
    assert target.current_weight_date == date(2026, 9, 14)


def test_household_aggregation_sums_compatible_member_targets():
    s = standard()
    as_of = date(2026, 9, 15)
    a = derive_member_target(profile("m1"), s, as_of)
    b = derive_member_target(profile("m2", sex=Sex.MALE), s, as_of)
    household = aggregate_household_target("h1", (a, b))
    protein = next(item for item in household.references if item.nutrient_measure == "PROT625")
    assert protein.lower_30d == Decimal("3360")
    assert household.energy_kcal_30d == a.energy_kcal_30d + b.energy_kcal_30d
