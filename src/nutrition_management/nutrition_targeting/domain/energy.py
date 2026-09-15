from datetime import date
from decimal import Decimal

from .model import NutritionProfile, Sex, UnsupportedSliceCapability, chronological_age_years


def adult_maintenance_energy_kcal_per_day(profile: NutritionProfile, derivation_date: date) -> Decimal:
    age = chronological_age_years(profile.date_of_birth, derivation_date)
    if age < 19:
        raise UnsupportedSliceCapability("age path is outside this implementation slice")
    if profile.current_weight_date > derivation_date:
        raise ValueError("current_weight_date must not be later than derivation_date")

    if profile.pal_activity_adjustment_applied:
        if not Decimal("1.5") <= profile.pal <= Decimal("2.7"):
            raise ValueError("activity-adjusted PAL must lie within 1.5-2.7")
    elif not Decimal("1.2") <= profile.pal <= Decimal("2.4"):
        raise ValueError("unadjusted PAL must lie within 1.2-2.4")

    if profile.target_weight_kg is not None and profile.target_weight_kg != profile.current_weight_kg:
        if profile.target_date is None:
            pass
        elif profile.target_date <= derivation_date:
            raise ValueError("active target_date must be later than derivation_date")
        else:
            raise UnsupportedSliceCapability("active weight-goal adjustment is outside this implementation slice")

    weight = profile.current_weight_kg
    age_decimal = Decimal(age)
    if profile.sex == Sex.FEMALE:
        ree = (Decimal("0.047") * weight - Decimal("0.01452") * age_decimal + Decimal("3.21")) * Decimal(239)
    else:
        ree = (
            Decimal("0.047") * weight
            + Decimal("1.009")
            - Decimal("0.01452") * age_decimal
            + Decimal("3.21")
        ) * Decimal(239)
    return ree * profile.pal
