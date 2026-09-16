from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.domain.model import TOP_LEVEL_CATEGORIES


@dataclass(frozen=True)
class ComponentDefinition:
    component_code: str
    name_de: str
    name_en: str
    unit: str
    group_de: str | None = None
    group_en: str | None = None
    formula: str | None = None
    formula_application: str | None = None

    def __post_init__(self) -> None:
        if not self.component_code:
            raise ValueError("component_code is required")
        if not self.name_de or not self.name_en:
            raise ValueError("component names are required")
        if not self.unit:
            raise ValueError("component unit is required")


@dataclass(frozen=True)
class SourceNutrientEvidence:
    component_code: str
    status: NutrientEvidenceStatus
    amount_per_100g: Decimal | None
    source_value_text: str
    value_origin: str
    source_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.component_code:
            raise ValueError("component_code is required")
        if not self.source_value_text:
            raise ValueError("explicit nutrient evidence requires source_value_text")
        if not self.value_origin:
            raise ValueError("explicit nutrient evidence requires value_origin")
        if self.status == NutrientEvidenceStatus.MISSING:
            raise ValueError("missing nutrient evidence is represented by absence, not an explicit row")
        if self.status in {NutrientEvidenceStatus.KNOWN, NutrientEvidenceStatus.ZERO}:
            if self.amount_per_100g is None:
                raise ValueError("known/zero nutrient evidence requires a numeric amount")
            if not self.amount_per_100g.is_finite() or self.amount_per_100g < 0:
                raise ValueError("nutrient amount must be finite and non-negative")
        elif self.amount_per_100g is not None:
            raise ValueError("trace nutrient evidence must not fabricate a numeric amount")
        if self.status == NutrientEvidenceStatus.ZERO and self.amount_per_100g != Decimal(0):
            raise ValueError("zero nutrient evidence must contain numeric zero")


@dataclass(frozen=True)
class SourceFood:
    source_code: str
    name_de: str
    name_en: str | None
    category: str
    nutrients: tuple[SourceNutrientEvidence, ...]

    def __post_init__(self) -> None:
        if not self.source_code:
            raise ValueError("source food code is required")
        if not self.name_de:
            raise ValueError("source food name is required")
        if self.category not in TOP_LEVEL_CATEGORIES:
            raise ValueError(f"unsupported top-level food category: {self.category}")
        component_codes = [item.component_code for item in self.nutrients]
        if len(component_codes) != len(set(component_codes)):
            raise ValueError("source food nutrient component codes must be unique")

    @property
    def base_food_id(self) -> str:
        return f"bls:4.0:{self.source_code}"


@dataclass(frozen=True)
class FoodSourceDataset:
    source_id: str
    source_name: str
    source_version: str
    source_digest: str
    package_digest: str
    doi: str
    license: str
    source_url: str
    attribution: str
    components: tuple[ComponentDefinition, ...]
    foods: tuple[SourceFood, ...]

    def __post_init__(self) -> None:
        required = {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_version": self.source_version,
            "source_digest": self.source_digest,
            "package_digest": self.package_digest,
            "doi": self.doi,
            "license": self.license,
            "source_url": self.source_url,
            "attribution": self.attribution,
        }
        for field, value in required.items():
            if not value:
                raise ValueError(f"{field} is required")

        component_codes = [item.component_code for item in self.components]
        if len(component_codes) != len(set(component_codes)):
            raise ValueError("component codes must be unique inside one source dataset")
        food_codes = [item.source_code for item in self.foods]
        if len(food_codes) != len(set(food_codes)):
            raise ValueError("food source codes must be unique inside one source dataset")

        known_components = set(component_codes)
        for food in self.foods:
            unknown = {item.component_code for item in food.nutrients} - known_components
            if unknown:
                raise ValueError(
                    f"food {food.source_code} references unknown components: {sorted(unknown)}"
                )
