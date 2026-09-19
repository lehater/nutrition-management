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
    BELOW_DETECTION_OR_QUANTIFICATION_LIMIT = "below_detection_or_quantification_limit"
    MISSING = "missing"

    @property
    def is_quantitative(self) -> bool:
        return self in {NutrientEvidenceStatus.KNOWN, NutrientEvidenceStatus.ZERO}


@dataclass(frozen=True)
class NutrientFact:
    measure: str
    status: NutrientEvidenceStatus
    amount_per_100g: Decimal | None


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
