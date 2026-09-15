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
    pal_activity_adjustment_applied: bool = False
    target_weight_kg: Decimal | None = None
    target_date: date | None = None

    def __post_init__(self) -> None:
        if self.height_m <= 0:
            raise ValueError("height must be positive")
        if self.current_weight_kg <= 0:
            raise ValueError("current weight must be positive")
        if self.target_weight_kg is not None and self.target_weight_kg <= 0:
            raise ValueError("target weight must be positive")


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

    def __post_init__(self) -> None:
        if not self.reference_id or not self.nutrient_measure:
            raise ValueError("reference identity and nutrient measure are required")
        for value in (self.lower, self.upper, self.point):
            if value is not None and value < 0:
                raise ValueError("reference values must be non-negative")

        if self.kind in {ReferenceKind.ADEQUACY_FLOOR, ReferenceKind.LOWER_BOUND}:
            if self.lower is None or self.lower <= 0 or self.upper is not None or self.point is not None:
                raise ValueError("lower-bound reference requires only a positive lower value")
        elif self.kind == ReferenceKind.UPPER_BOUND:
            if self.upper is None or self.upper <= 0 or self.lower is not None or self.point is not None:
                raise ValueError("upper-bound reference requires only a positive upper value")
        elif self.kind == ReferenceKind.INTERVAL:
            if (
                self.lower is None
                or self.upper is None
                or self.lower <= 0
                or self.upper <= 0
                or self.lower > self.upper
                or self.point is not None
            ):
                raise ValueError("interval reference requires a positive ordered lower/upper pair")
        elif self.kind == ReferenceKind.POINT:
            if self.point is None or self.point <= 0 or self.lower is not None or self.upper is not None:
                raise ValueError("point reference requires only a positive point value")

        if self.basis == ReferenceBasis.PERCENT_ENERGY:
            if self.energy_kcal_per_g is None or self.energy_kcal_per_g <= 0:
                raise ValueError("percent-energy reference requires a positive energy factor")
        elif self.energy_kcal_per_g is not None:
            raise ValueError("energy factor is only valid for percent-energy references")


@dataclass(frozen=True)
class SafetyDefinition:
    reference_id: str
    nutrient_measure: str
    daily_upper: Decimal

    def __post_init__(self) -> None:
        if not self.reference_id or not self.nutrient_measure:
            raise ValueError("safety reference identity and nutrient measure are required")
        if self.daily_upper <= 0:
            raise ValueError("safety daily upper must be positive")


@dataclass(frozen=True)
class NutritionStandardSet:
    version: str
    references: tuple[ReferenceDefinition, ...]
    safety_limits: tuple[SafetyDefinition, ...] = ()

    def __post_init__(self) -> None:
        if not self.version:
            raise ValueError("standard version is required")
        reference_ids = [item.reference_id for item in self.references]
        safety_ids = [item.reference_id for item in self.safety_limits]
        if len(reference_ids) != len(set(reference_ids)):
            raise ValueError("reference ids must be unique within a standard version")
        if len(safety_ids) != len(set(safety_ids)):
            raise ValueError("safety reference ids must be unique within a standard version")


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
    current_weight_kg: Decimal
    current_weight_date: date
    pal: Decimal
    pal_activity_adjustment_applied: bool
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
