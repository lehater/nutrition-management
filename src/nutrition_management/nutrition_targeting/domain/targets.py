from collections import defaultdict
from datetime import date
from decimal import Decimal

from .energy import adult_maintenance_energy_kcal_per_day
from .model import (
    AgeBoundary,
    AgeUnit,
    ApplicableWeightRule,
    MappingStatus,
    MemberNutritionTarget,
    MemberSafetyLimit,
    NutritionProfile,
    NutritionStandardSet,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceGap,
    ReferenceGapState,
    ReferenceScope,
    ResolvedReference,
    SafetyDefinition,
    SafetyGap,
    SafetyGapState,
    completed_calendar_months,
    chronological_age_years,
)

_DAYS = Decimal(30)
_MASS_TO_G = {
    "g": Decimal(1),
    "mg": Decimal("0.001"),
    "µg": Decimal("0.000001"),
}


def _age_value(profile: NutritionProfile, derivation_date: date, boundary: AgeBoundary) -> int:
    if boundary.unit == AgeUnit.YEARS:
        return chronological_age_years(profile.date_of_birth, derivation_date)
    if boundary.unit == AgeUnit.MONTHS:
        return completed_calendar_months(profile.date_of_birth, derivation_date)
    raise ValueError(f"unsupported age unit: {boundary.unit}")


def _known_applicability_matches(definition, profile: NutritionProfile, derivation_date: date) -> bool:
    applicability = definition.applicability
    if applicability.sex is not None and applicability.sex != profile.sex:
        return False
    if applicability.min_age is not None:
        if _age_value(profile, derivation_date, applicability.min_age) < applicability.min_age.value:
            return False
    if applicability.max_age is not None:
        if _age_value(profile, derivation_date, applicability.max_age) >= applicability.max_age.value:
            return False
    return True


def _select_family(
    *,
    family_id: str,
    definitions: tuple,
    profile: NutritionProfile,
    derivation_date: date,
    applicability_facts: dict[str, str] | None = None,
):
    facts = {} if applicability_facts is None else applicability_facts
    candidates = tuple(
        item
        for item in definitions
        if item.scope == ReferenceScope.ACTIVE and _known_applicability_matches(item, profile, derivation_date)
    )
    if not candidates:
        return None, ReferenceGap(
            member_id=profile.member_id,
            family_id=family_id,
            state=ReferenceGapState.SOURCE_INAPPLICABLE,
            reason="known member facts are outside active source applicability",
        )

    compatible = []
    for item in candidates:
        rejected = False
        for requirement in item.applicability.requirements:
            actual = facts.get(requirement.dimension)
            if actual is not None and actual != requirement.value:
                rejected = True
                break
        if not rejected:
            compatible.append(item)

    if not compatible:
        return None, ReferenceGap(
            member_id=profile.member_id,
            family_id=family_id,
            state=ReferenceGapState.SOURCE_INAPPLICABLE,
            reason="known applicability facts do not match an active source variant",
        )

    unresolved = {
        requirement.dimension
        for item in compatible
        for requirement in item.applicability.requirements
        if requirement.dimension not in facts
    }
    if unresolved:
        return None, ReferenceGap(
            member_id=profile.member_id,
            family_id=family_id,
            state=ReferenceGapState.UNSUPPORTED_APPLICABILITY,
            missing_dimensions=tuple(sorted(unresolved)),
            candidate_reference_ids=tuple(sorted(item.reference_id for item in compatible)),
            reason="source variant selection requires applicability facts not owned by the current MVP profile",
        )

    if len(compatible) != 1:
        ids = sorted(item.reference_id for item in compatible)
        raise ValueError(f"{family_id}: ambiguous active source variants after applicability resolution: {ids}")
    return compatible[0], None


def _applicable_weight(
    definition: ReferenceDefinition,
    profile: NutritionProfile,
) -> tuple[Decimal | None, str | None]:
    rule = definition.applicable_weight_rule or ApplicableWeightRule.CURRENT_WEIGHT
    if rule == ApplicableWeightRule.CURRENT_WEIGHT:
        return profile.current_weight_kg, None
    if rule == ApplicableWeightRule.DGE_ADULT_PROTEIN:
        bmi = profile.current_weight_kg / (profile.height_m * profile.height_m)
        if Decimal("18.5") <= bmi < Decimal("25.0"):
            return profile.current_weight_kg, None
        if Decimal("25.0") <= bmi < Decimal("30.0"):
            return Decimal(22) * profile.height_m * profile.height_m, None
        return None, f"DGE adult protein general reference is inapplicable at BMI {bmi}"
    raise ValueError(f"unsupported applicable weight rule: {rule}")


def _daily_value(
    definition: ReferenceDefinition,
    raw: Decimal | None,
    profile: NutritionProfile,
    energy: Decimal,
) -> tuple[Decimal | None, str | None]:
    if raw is None:
        return None, None
    if definition.basis == ReferenceBasis.ABSOLUTE_DAILY:
        return raw, None
    if definition.basis == ReferenceBasis.PER_KG_DAILY:
        weight, reason = _applicable_weight(definition, profile)
        return (None, reason) if weight is None else (raw * weight, None)
    if definition.basis == ReferenceBasis.PERCENT_ENERGY:
        if definition.energy_kcal_per_g is None or definition.energy_kcal_per_g <= 0:
            raise ValueError(f"{definition.reference_id}: missing energy factor")
        fraction = raw / Decimal(100) if definition.source_unit == "percent_energy" else raw
        return energy * fraction / definition.energy_kcal_per_g, None
    if definition.basis == ReferenceBasis.PER_1000_KCAL:
        return raw * energy / Decimal(1000), None
    raise ValueError(f"unsupported reference basis: {definition.basis}")


def _result_unit(definition: ReferenceDefinition) -> str | None:
    if definition.basis == ReferenceBasis.PERCENT_ENERGY:
        return "g"
    return definition.source_unit


def _convert_unit(value: Decimal | None, source_unit: str | None, target_unit: str | None) -> Decimal | None:
    if value is None or source_unit is None or target_unit is None or source_unit == target_unit:
        return value
    if source_unit in _MASS_TO_G and target_unit in _MASS_TO_G:
        return value * _MASS_TO_G[source_unit] / _MASS_TO_G[target_unit]
    if source_unit == "kJ" and target_unit == "kcal":
        return value / Decimal("4.184")
    if source_unit == "kcal" and target_unit == "kJ":
        return value * Decimal("4.184")
    raise ValueError(f"unsupported exact unit conversion: {source_unit} -> {target_unit}")


def _safety_gap_from_reference_gap(gap: ReferenceGap) -> SafetyGap:
    state = SafetyGapState(gap.state.value)
    return SafetyGap(
        member_id=gap.member_id,
        family_id=gap.family_id,
        state=state,
        missing_dimensions=gap.missing_dimensions,
        candidate_reference_ids=gap.candidate_reference_ids,
        reason=gap.reason,
    )


def _selected_safety_limits(
    profile: NutritionProfile,
    standard: NutritionStandardSet,
    derivation_date: date,
    applicability_facts: dict[str, str] | None,
) -> tuple[tuple[MemberSafetyLimit, ...], tuple[SafetyGap, ...]]:
    grouped: dict[str, list[SafetyDefinition]] = defaultdict(list)
    for item in standard.safety_limits:
        if item.scope == ReferenceScope.ACTIVE:
            grouped[item.resolved_family_id].append(item)

    selected: list[MemberSafetyLimit] = []
    gaps: list[SafetyGap] = []
    for family_id, rows in sorted(grouped.items()):
        definition, selection_gap = _select_family(
            family_id=family_id,
            definitions=tuple(rows),
            profile=profile,
            derivation_date=derivation_date,
            applicability_facts=applicability_facts,
        )
        if selection_gap is not None:
            gaps.append(_safety_gap_from_reference_gap(selection_gap))
            continue
        assert definition is not None

        # Backward compatibility for the test-only first slice. Production mvp-v1
        # supplies a complete safety mapping registry and never falls through here.
        mapping = standard.safety_mapping_for_family(family_id)
        if mapping is None and not standard.safety_mappings:
            measure = definition.nutrient_measure
            daily_upper = definition.daily_upper
        else:
            if mapping is None:
                raise ValueError(f"missing safety mapping decision for active family {family_id}")
            if mapping.status == MappingStatus.UNSUPPORTED:
                gaps.append(
                    SafetyGap(
                        member_id=profile.member_id,
                        family_id=family_id,
                        state=SafetyGapState.UNSUPPORTED_MAPPING,
                        candidate_reference_ids=(definition.reference_id,),
                        reason=mapping.reason,
                    )
                )
                continue
            measure = mapping.nutrient_measure
            assert measure is not None
            daily_upper = _convert_unit(definition.daily_upper, definition.source_unit, mapping.canonical_unit)
            assert daily_upper is not None

        selected.append(
            MemberSafetyLimit(
                member_id=profile.member_id,
                reference_id=definition.reference_id,
                nutrient_measure=measure,
                daily_upper=daily_upper,
            )
        )
    return tuple(selected), tuple(gaps)


def derive_member_target(
    profile: NutritionProfile,
    standard: NutritionStandardSet,
    derivation_date: date,
    *,
    applicability_facts: dict[str, str] | None = None,
):
    energy = adult_maintenance_energy_kcal_per_day(profile, derivation_date)
    grouped: dict[str, list[ReferenceDefinition]] = defaultdict(list)
    for definition in standard.references:
        if definition.scope == ReferenceScope.ACTIVE:
            grouped[definition.resolved_family_id].append(definition)

    refs: list[ResolvedReference] = []
    gaps: list[ReferenceGap] = []
    for family_id, rows in sorted(grouped.items()):
        definition, gap = _select_family(
            family_id=family_id,
            definitions=tuple(rows),
            profile=profile,
            derivation_date=derivation_date,
            applicability_facts=applicability_facts,
        )
        if gap is not None:
            gaps.append(gap)
            continue
        assert definition is not None

        mapping = standard.mapping_for_family(family_id)
        if mapping is not None and mapping.status == MappingStatus.UNSUPPORTED:
            gaps.append(
                ReferenceGap(
                    member_id=profile.member_id,
                    family_id=family_id,
                    state=ReferenceGapState.UNSUPPORTED_MAPPING,
                    candidate_reference_ids=(definition.reference_id,),
                    reason=mapping.reason,
                )
            )
            continue
        if not definition.lower_inclusive or not definition.upper_inclusive:
            gaps.append(
                ReferenceGap(
                    member_id=profile.member_id,
                    family_id=family_id,
                    state=ReferenceGapState.UNSUPPORTED_TARGET_SHAPE,
                    candidate_reference_ids=(definition.reference_id,),
                    reason="current Purchase Planning target shape cannot represent an open source bound exactly",
                )
            )
            continue
        measure = definition.nutrient_measure if mapping is None else mapping.nutrient_measure
        assert measure is not None

        lower, weight_error = _daily_value(definition, definition.lower, profile, energy)
        upper, upper_weight_error = _daily_value(definition, definition.upper, profile, energy)
        point, point_weight_error = _daily_value(definition, definition.point, profile, energy)
        weight_error = weight_error or upper_weight_error or point_weight_error
        if weight_error is not None:
            gaps.append(
                ReferenceGap(
                    member_id=profile.member_id,
                    family_id=family_id,
                    state=ReferenceGapState.SOURCE_INAPPLICABLE,
                    candidate_reference_ids=(definition.reference_id,),
                    reason=weight_error,
                )
            )
            continue

        target_unit = None if mapping is None else mapping.canonical_unit
        source_result_unit = _result_unit(definition)
        lower = _convert_unit(lower, source_result_unit, target_unit)
        upper = _convert_unit(upper, source_result_unit, target_unit)
        point = _convert_unit(point, source_result_unit, target_unit)

        refs.append(
            ResolvedReference(
                reference_id=definition.reference_id,
                family_id=family_id,
                nutrient_measure=measure,
                kind=definition.kind,
                lower_30d=None if lower is None else lower * _DAYS,
                upper_30d=None if upper is None else upper * _DAYS,
                point_30d=None if point is None else point * _DAYS,
            )
        )

    safety, safety_gaps = _selected_safety_limits(profile, standard, derivation_date, applicability_facts)
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
        reference_gaps=tuple(gaps),
        safety_gaps=safety_gaps,
    )
