from decimal import Decimal

import pytest

from nutrition_management.food_knowledge.domain.model import BaseFood, NutrientEvidence, NutrientStatus


def test_known_nutrient_amount_cannot_be_negative():
    with pytest.raises(ValueError, match="non-negative"):
        NutrientEvidence("ENERCC", NutrientStatus.KNOWN, Decimal("-1"))


@pytest.mark.parametrize(
    "status",
    [
        NutrientStatus.TRACE,
        NutrientStatus.BELOW_QUANTIFICATION_LIMIT,
        NutrientStatus.BELOW_DETECTION_LIMIT,
        NutrientStatus.MISSING,
    ],
)
def test_non_quantitative_evidence_cannot_fabricate_numeric_amount(status):
    with pytest.raises(ValueError, match="non-quantitative"):
        NutrientEvidence("FIBT", status, Decimal("0"))


def test_only_known_and_zero_evidence_are_quantitatively_known():
    assert NutrientEvidence("ENERCC", NutrientStatus.KNOWN, Decimal("1")).is_quantitatively_known
    assert NutrientEvidence("NA", NutrientStatus.ZERO, Decimal(0)).is_quantitatively_known
    assert not NutrientEvidence(
        "NA", NutrientStatus.BELOW_QUANTIFICATION_LIMIT
    ).is_quantitatively_known
    assert not NutrientEvidence("NA", NutrientStatus.BELOW_DETECTION_LIMIT).is_quantitatively_known


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
