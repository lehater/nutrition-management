from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class NutrientStatus(StrEnum):
    KNOWN = "known"
    ZERO = "zero"
    TRACE = "trace"
    MISSING = "missing"


@dataclass(frozen=True)
class NutrientEvidence:
    measure: str
    status: NutrientStatus
    amount_per_100g: Decimal | None = None

    def __post_init__(self) -> None:
        if self.status in {NutrientStatus.KNOWN, NutrientStatus.ZERO} and self.amount_per_100g is None:
            raise ValueError("known/zero nutrient evidence requires a numeric amount")
        if self.status == NutrientStatus.ZERO and self.amount_per_100g != Decimal(0):
            raise ValueError("zero nutrient evidence must contain numeric zero")
        if self.status in {NutrientStatus.TRACE, NutrientStatus.MISSING} and self.amount_per_100g is not None:
            raise ValueError("trace/missing nutrient evidence must not fabricate a numeric amount")

    @property
    def is_quantitatively_known(self) -> bool:
        return self.status in {NutrientStatus.KNOWN, NutrientStatus.ZERO}


@dataclass(frozen=True)
class BaseFood:
    base_food_id: str
    name: str
    category: str
    nutrients: tuple[NutrientEvidence, ...]
    source_name: str
    source_version: str | None = None

    def nutrient(self, measure: str) -> NutrientEvidence:
        for item in self.nutrients:
            if item.measure == measure:
                return item
        return NutrientEvidence(measure=measure, status=NutrientStatus.MISSING)
