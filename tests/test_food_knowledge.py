from decimal import Decimal

import pytest

from nutrition_management.food_knowledge.domain.model import BaseFood, NutrientEvidence, NutrientStatus


def test_known_nutrient_amount_cannot_be_negative():
    with pytest.raises(ValueError, match="non-negative"):
        NutrientEvidence("ENERCC", NutrientStatus.KNOWN, Decimal("-1"))


def test_base_food_rejects_duplicate_component_and_unknown_primary_category():
    energy = NutrientEvidence("ENERCC", NutrientStatus.KNOWN, Decimal("100"))
    with pytest.raises(ValueError, match="unique"):
        BaseFood(
            "food",
            "Food",
            "fruit_and_vegetables",
            (energy, energy),
            "test",
        )
    with pytest.raises(ValueError, match="top-level food category"):
        BaseFood("food", "Food", "store_aisle_42", (energy,), "test")
