from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class NutrientEvidenceStatus(StrEnum):
    KNOWN = "known"
    ZERO = "zero"
    TRACE = "trace"
    BELOW_QUANTIFICATION_LIMIT = "below_quantification_limit"
    BELOW_DETECTION_LIMIT = "below_detection_limit"
    MISSING = "missing"

    @property
    def is_quantitatively_known(self) -> bool:
        return self in {NutrientEvidenceStatus.KNOWN, NutrientEvidenceStatus.ZERO}


@dataclass(frozen=True)
class NutrientFact:
    measure: str
    status: NutrientEvidenceStatus
    amount_per_100g: Decimal | None

    def __post_init__(self) -> None:
        if self.status.is_quantitatively_known and self.amount_per_100g is None:
            raise ValueError("known/zero nutrient evidence requires a numeric amount")
        if self.amount_per_100g is not None and self.amount_per_100g < 0:
            raise ValueError("nutrient amount must be non-negative")
        if self.status == NutrientEvidenceStatus.ZERO and self.amount_per_100g != Decimal(0):
            raise ValueError("zero nutrient evidence must contain numeric zero")
        if not self.status.is_quantitatively_known and self.amount_per_100g is not None:
            raise ValueError("non-quantitative nutrient evidence must not fabricate a numeric amount")


@dataclass(frozen=True)
class FoodFact:
    base_food_id: str
    name: str
    category: str
    nutrients: tuple[NutrientFact, ...]
    source_name: str
    source_version: str | None

    def nutrient(self, measure: str) -> NutrientFact:
        for item in self.nutrients:
            if item.measure == measure:
                return item
        return NutrientFact(measure, NutrientEvidenceStatus.MISSING, None)
