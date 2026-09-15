from decimal import Decimal

from .energy import adult_maintenance_energy_kcal_per_day
from .model import (
    MemberNutritionTarget,
    MemberSafetyLimit,
    NutritionProfile,
    NutritionStandardSet,
    ReferenceBasis,
    ResolvedReference,
    chronological_age_years,
)

_DAYS = Decimal(30)


def _daily_value(definition, raw: Decimal | None, profile: NutritionProfile, energy: Decimal) -> Decimal | None:
    if raw is None:
        return None
    if definition.basis == ReferenceBasis.ABSOLUTE_DAILY:
        return raw
    if definition.basis == ReferenceBasis.PER_KG_DAILY:
        return raw * profile.current_weight_kg
    if definition.basis == ReferenceBasis.PERCENT_ENERGY:
        if definition.energy_kcal_per_g is None or definition.energy_kcal_per_g <= 0:
            raise ValueError(f"{definition.reference_id}: missing energy factor")
        return energy * raw / definition.energy_kcal_per_g
    raise ValueError(f"unsupported reference basis: {definition.basis}")


def derive_member_target(profile: NutritionProfile, standard: NutritionStandardSet, derivation_date):
    energy = adult_maintenance_energy_kcal_per_day(profile, derivation_date)
    refs = []
    for definition in standard.references:
        lower = _daily_value(definition, definition.lower, profile, energy)
        upper = _daily_value(definition, definition.upper, profile, energy)
        point = _daily_value(definition, definition.point, profile, energy)
        refs.append(
            ResolvedReference(
                reference_id=definition.reference_id,
                nutrient_measure=definition.nutrient_measure,
                kind=definition.kind,
                lower_30d=None if lower is None else lower * _DAYS,
                upper_30d=None if upper is None else upper * _DAYS,
                point_30d=None if point is None else point * _DAYS,
            )
        )

    safety = tuple(
        MemberSafetyLimit(
            member_id=profile.member_id,
            reference_id=item.reference_id,
            nutrient_measure=item.nutrient_measure,
            daily_upper=item.daily_upper,
        )
        for item in standard.safety_limits
    )
    return MemberNutritionTarget(
        member_id=profile.member_id,
        derivation_date=derivation_date,
        standard_version=standard.version,
        age_years=chronological_age_years(profile.date_of_birth, derivation_date),
        current_weight_kg=profile.current_weight_kg,
        current_weight_date=profile.current_weight_date,
        pal=profile.pal,
        pal_activity_adjustment_applied=profile.pal_activity_adjustment_applied,
        energy_kcal_30d=energy * _DAYS,
        references=tuple(refs),
        safety_limits=safety,
    )
