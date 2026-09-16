from __future__ import annotations

from nutrition_management.nutrition_targeting.application.contracts import (
    HouseholdTargetFact,
    MemberSafetyFact,
    MemberTargetProvenanceFact,
    SafetyCoverageFact,
    TargetCoverageFact,
    TargetFact,
)
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
        member_safety_limits=tuple(
            MemberSafetyFact(
                member_id=limit.member_id,
                reference_id=limit.reference_id,
                measure=limit.nutrient_measure,
                daily_upper=limit.daily_upper,
            )
            for member in members
            for limit in member.safety_limits
        ),
        member_provenance=tuple(
            MemberTargetProvenanceFact(
                member_id=member.member_id,
                age_years=member.age_years,
                current_weight_kg=member.current_weight_kg,
                current_weight_date=member.current_weight_date,
                pal=member.pal,
                pal_activity_adjustment_applied=member.pal_activity_adjustment_applied,
            )
            for member in members
        ),
        target_coverage_gaps=tuple(
            TargetCoverageFact(
                member_id=gap.member_id,
                family_id=gap.family_id,
                state=gap.state.value,
                missing_dimensions=gap.missing_dimensions,
                candidate_reference_ids=gap.candidate_reference_ids,
                reason=gap.reason,
            )
            for gap in household.reference_gaps
        ),
        safety_coverage_gaps=tuple(
            SafetyCoverageFact(
                member_id=gap.member_id,
                family_id=gap.family_id,
                state=gap.state.value,
                reason=gap.reason,
            )
            for gap in household.safety_gaps
        ),
    )
