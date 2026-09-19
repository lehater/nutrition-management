from __future__ import annotations

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.application.queries import (
    theoretical_foods_with_positive_measure,
)
from nutrition_management.food_knowledge.infrastructure.repository import (
    FoodKnowledgeRepository,
)
from nutrition_management.purchase_planning.domain.model import TheoreticalFoodCandidate


class FoodKnowledgeGapSuggestionSource:
    def __init__(self, engine):
        self._engine = engine

    def candidates_for_measure(
        self,
        measure: str,
    ) -> tuple[TheoreticalFoodCandidate, ...]:
        with self._engine.connect() as connection:
            repository = FoodKnowledgeRepository(connection)
            foods = theoretical_foods_with_positive_measure(repository, measure)
            result: list[TheoreticalFoodCandidate] = []
            for food in foods:
                nutrient = food.nutrient(measure)
                if nutrient.amount_per_100g is None:
                    continue
                energy = food.nutrient("ENERCC")
                energy_amount = (
                    energy.amount_per_100g
                    if (
                        energy.status == NutrientEvidenceStatus.KNOWN
                        and energy.amount_per_100g is not None
                        and energy.amount_per_100g > 0
                    )
                    else None
                )
                result.append(
                    TheoreticalFoodCandidate(
                        base_food_id=food.base_food_id,
                        food_name=food.name,
                        category=food.category,
                        measure_amount_per_100g=nutrient.amount_per_100g,
                        energy_amount_per_100g=energy_amount,
                        source_name=food.source_name,
                        source_version=food.source_version,
                    )
                )
            return tuple(result)
