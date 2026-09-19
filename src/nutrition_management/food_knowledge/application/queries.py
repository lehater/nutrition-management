from __future__ import annotations

from nutrition_management.food_knowledge.application.contracts import (
    FoodFact,
    NutrientEvidenceStatus,
)


def theoretical_foods_with_positive_measure(repository, measure: str) -> tuple[FoodFact, ...]:
    """Publish theoretical foods with deterministic positive evidence for one measure."""
    if not measure:
        raise ValueError("measure is required")

    result: list[FoodFact] = []
    for food in repository.all_foods():
        evidence = food.nutrient(measure)
        if (
            evidence.status == NutrientEvidenceStatus.KNOWN
            and evidence.amount_per_100g is not None
            and evidence.amount_per_100g > 0
        ):
            result.append(food)
    return tuple(sorted(result, key=lambda item: item.base_food_id))
