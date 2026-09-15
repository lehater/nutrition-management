from collections import defaultdict
from decimal import Decimal

from .model import HouseholdNutritionTarget, MemberNutritionTarget, ReferenceKind, ResolvedReference


def aggregate_household_target(household_id: str, member_targets: tuple[MemberNutritionTarget, ...]) -> HouseholdNutritionTarget:
    if not member_targets:
        raise ValueError("household must have at least one member target")

    dates = {item.derivation_date for item in member_targets}
    versions = {item.standard_version for item in member_targets}
    if len(dates) != 1 or len(versions) != 1:
        raise ValueError("member targets must share derivation date and standard version")

    grouped: dict[tuple[str, ReferenceKind], list[ResolvedReference]] = defaultdict(list)
    for member in member_targets:
        for ref in member.references:
            grouped[(ref.nutrient_measure, ref.kind)].append(ref)

    refs: list[ResolvedReference] = []
    for (measure, kind), items in sorted(grouped.items(), key=lambda entry: (entry[0][0], entry[0][1].value)):
        def total(attr: str):
            values = [getattr(item, attr) for item in items]
            if all(value is None for value in values):
                return None
            if any(value is None for value in values):
                raise ValueError(f"incompatible target shape for {measure}/{kind}")
            return sum(values, Decimal(0))

        refs.append(
            ResolvedReference(
                reference_id="household:" + "+".join(item.reference_id for item in items),
                nutrient_measure=measure,
                kind=kind,
                lower_30d=total("lower_30d"),
                upper_30d=total("upper_30d"),
                point_30d=total("point_30d"),
            )
        )

    return HouseholdNutritionTarget(
        household_id=household_id,
        derivation_date=next(iter(dates)),
        standard_version=next(iter(versions)),
        energy_kcal_30d=sum((item.energy_kcal_30d for item in member_targets), Decimal(0)),
        references=tuple(refs),
        member_targets=member_targets,
    )
