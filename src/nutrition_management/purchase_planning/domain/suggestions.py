from __future__ import annotations

from decimal import Decimal

from .model import (
    CORE_CATEGORIES,
    GapSuggestion,
    PlanningInputSnapshot,
    PurchasePlan,
    TargetKind,
    TheoreticalFoodCandidate,
)


def positive_gap_measures(
    snapshot: PlanningInputSnapshot,
    plan: PurchasePlan,
) -> tuple[str, ...]:
    """Return mapped positive gaps that are eligible for theoretical food suggestions."""
    assessments = {item.measure: item for item in plan.assessments}
    result: list[str] = []

    energy = assessments.get("ENERCC")
    if (
        energy is not None
        and energy.penalty > 0
        and energy.amount < snapshot.energy_target_kcal * Decimal("0.95")
    ):
        result.append("ENERCC")

    for target in snapshot.targets:
        if target.kind not in {TargetKind.ADEQUACY_FLOOR, TargetKind.LOWER_BOUND}:
            continue
        assessment = assessments.get(target.measure)
        if assessment is not None and assessment.penalty > 0:
            result.append(target.measure)

    return tuple(dict.fromkeys(result))


def rank_gap_suggestions(
    *,
    measure: str,
    foods: tuple[TheoreticalFoodCandidate, ...],
    represented_categories: tuple[str, ...],
) -> tuple[GapSuggestion, ...]:
    represented = set(represented_categories)
    scored: list[tuple[tuple[object, ...], GapSuggestion]] = []

    for food in foods:
        if food.measure_amount_per_100g <= 0:
            continue

        per_100kcal: Decimal | None = None
        if (
            measure != "ENERCC"
            and food.energy_amount_per_100g is not None
            and food.energy_amount_per_100g > 0
        ):
            per_100kcal = (
                food.measure_amount_per_100g
                * Decimal(100)
                / food.energy_amount_per_100g
            )

        suggestion = GapSuggestion(
            measure=measure,
            base_food_id=food.base_food_id,
            food_name=food.food_name,
            category=food.category,
            amount_per_100g=food.measure_amount_per_100g,
            amount_per_100kcal=per_100kcal,
            source_name=food.source_name,
            source_version=food.source_version,
        )

        variety_preferred = (
            food.category in CORE_CATEGORIES and food.category not in represented
        )
        if measure == "ENERCC":
            key = (
                -food.measure_amount_per_100g,
                0 if variety_preferred else 1,
                food.base_food_id,
            )
        else:
            key = (
                0 if per_100kcal is not None else 1,
                -(per_100kcal or Decimal(0)),
                -food.measure_amount_per_100g,
                0 if variety_preferred else 1,
                food.base_food_id,
            )
        scored.append((key, suggestion))

    return tuple(item for _, item in sorted(scored, key=lambda pair: pair[0]))
