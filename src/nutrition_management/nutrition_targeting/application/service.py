from __future__ import annotations

from nutrition_management.nutrition_targeting.application.contracts import HouseholdTargetFact, TargetFact
from nutrition_management.nutrition_targeting.domain.aggregation import aggregate_household_target
from nutrition_management.nutrition_targeting.domain.targets import derive_member_target


def derive_household_target_fact(repository, household_id: str, derivation_date) -> HouseholdTargetFact:
    profiles = repository.profiles_for_household(household_id)
    if not profiles:
        raise ValueError(f"unknown or empty household: {household_id}")
    standard = repository.active_standard()
    members = tuple(derive_member_target(profile, standard, derivation_date) for profile in profiles)
    household = aggregate_household_target(household_id, members)
    return HouseholdTargetFact(
        household_id=household.household_id,
        derivation_date=household.derivation_date,
        standard_version=household.standard_version,
        energy_kcal_30d=household.energy_kcal_30d,
        targets=tuple(
            TargetFact(
                measure=item.nutrient_measure,
                kind=item.kind.value,
                lower_30d=item.lower_30d,
                upper_30d=item.upper_30d,
                point_30d=item.point_30d,
            )
            for item in household.references
        ),
        member_ids=tuple(member.member_id for member in members),
    )
