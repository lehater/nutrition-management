from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class NutrientStatus(StrEnum):
    KNOWN = "known"
    ZERO = "zero"
    TRACE = "trace"
    BELOW_QUANTIFICATION_LIMIT = "below_quantification_limit"
    BELOW_DETECTION_LIMIT = "below_detection_limit"
    MISSING = "missing"

    @property
    def is_quantitatively_known(self) -> bool:
        return self in {NutrientStatus.KNOWN, NutrientStatus.ZERO}


TOP_LEVEL_CATEGORIES = frozenset(
    {
        "beverages",
        "fruit_and_vegetables",
        "legumes_nuts_seeds",
        "grains_cereal_products_potatoes",
        "oils_and_fats",
        "milk_and_dairy",
        "fish_meat_sausage_eggs",
        "other_or_composite",
    }
)


@dataclass(frozen=True)
class NutrientEvidence:
    measure: str
    status: NutrientStatus
    amount_per_100g: Decimal | None = None

    def __post_init__(self) -> None:
        if self.status.is_quantitatively_known and self.amount_per_100g is None:
            raise ValueError("known/zero nutrient evidence requires a numeric amount")
        if self.amount_per_100g is not None and self.amount_per_100g < 0:
            raise ValueError("nutrient amount must be non-negative")
        if self.status == NutrientStatus.ZERO and self.amount_per_100g != Decimal(0):
            raise ValueError("zero nutrient evidence must contain numeric zero")
        if not self.status.is_quantitatively_known and self.amount_per_100g is not None:
            raise ValueError("non-quantitative nutrient evidence must not fabricate a numeric amount")

    @property
    def is_quantitatively_known(self) -> bool:
        return self.status.is_quantitatively_known


@dataclass(frozen=True)
class BaseFood:
    base_food_id: str
    name: str
    category: str
    nutrients: tuple[NutrientEvidence, ...]
    source_name: str
    source_version: str | None = None

    def __post_init__(self) -> None:
        if self.category not in TOP_LEVEL_CATEGORIES:
            raise ValueError(f"unsupported top-level food category: {self.category}")
        measures = [item.measure for item in self.nutrients]
        if len(measures) != len(set(measures)):
            raise ValueError("base food nutrient measures must be unique")

    def nutrient(self, measure: str) -> NutrientEvidence:
        for item in self.nutrients:
            if item.measure == measure:
                return item
        return NutrientEvidence(measure=measure, status=NutrientStatus.MISSING)
