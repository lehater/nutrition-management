from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class UnsupportedSliceCapability(ValueError):
    """Accepted product behavior that is intentionally outside the authorized slice."""


class Sex(StrEnum):
    FEMALE = "female"
    MALE = "male"


class ReferenceKind(StrEnum):
    ADEQUACY_FLOOR = "adequacy_floor"
    LOWER_BOUND = "lower_bound"
    UPPER_BOUND = "upper_bound"
    INTERVAL = "interval"
    POINT = "point"


class ReferenceBasis(StrEnum):
    ABSOLUTE_DAILY = "absolute_daily"
    PER_KG_DAILY = "per_kg_daily"
    PERCENT_ENERGY = "percent_energy"


@dataclass(frozen=True)
class NutritionProfile:
    member_id: str
    date_of_birth: date
    sex: Sex
    height_m: Decimal
    current_weight_kg: Decimal
    current_weight_date: date
    pal: Decimal
    target_weight_kg: Decimal | None = None
    target_date: date | None = None


@dataclass(frozen=True)
class ReferenceDefinition:
    reference_id: str
    nutrient_measure: str
    kind: ReferenceKind
    basis: ReferenceBasis
    lower: Decimal | None = None
    upper: Decimal | None = None
    point: Decimal | None = None
    energy_kcal_per_g: Decimal | None = None


@dataclass(frozen=True)
class SafetyDefinition:
    reference_id: str
    nutrient_measure: str
    daily_upper: Decimal


@dataclass(frozen=True)
class NutritionStandardSet:
    version: str
    references: tuple[ReferenceDefinition, ...]
    safety_limits: tuple[SafetyDefinition, ...] = ()


@dataclass(frozen=True)
class ResolvedReference:
    reference_id: str
    nutrient_measure: str
    kind: ReferenceKind
    lower_30d: Decimal | None = None
    upper_30d: Decimal | None = None
    point_30d: Decimal | None = None


@dataclass(frozen=True)
class MemberSafetyLimit:
    member_id: str
    reference_id: str
    nutrient_measure: str
    daily_upper: Decimal


@dataclass(frozen=True)
class MemberNutritionTarget:
    member_id: str
    derivation_date: date
    standard_version: str
    age_years: int
    energy_kcal_30d: Decimal
    references: tuple[ResolvedReference, ...]
    safety_limits: tuple[MemberSafetyLimit, ...]


@dataclass(frozen=True)
class HouseholdNutritionTarget:
    household_id: str
    derivation_date: date
    standard_version: str
    energy_kcal_30d: Decimal
    references: tuple[ResolvedReference, ...]
    member_targets: tuple[MemberNutritionTarget, ...]


def chronological_age_years(date_of_birth: date, on_date: date) -> int:
    if date_of_birth > on_date:
        raise ValueError("date_of_birth must not be later than derivation date")
    years = on_date.year - date_of_birth.year
    if (on_date.month, on_date.day) < (date_of_birth.month, date_of_birth.day):
        years -= 1
    return years
