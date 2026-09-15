from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum


class TargetKind(StrEnum):
    ADEQUACY_FLOOR = "adequacy_floor"
    LOWER_BOUND = "lower_bound"
    UPPER_BOUND = "upper_bound"
    INTERVAL = "interval"
    POINT = "point"


class EvidenceStatus(StrEnum):
    KNOWN = "known"
    ZERO = "zero"
    TRACE = "trace"
    MISSING = "missing"


@dataclass(frozen=True)
class TargetDimension:
    measure: str
    kind: TargetKind
    lower: Decimal | None = None
    upper: Decimal | None = None
    point: Decimal | None = None


@dataclass(frozen=True)
class CandidateNutrient:
    measure: str
    status: EvidenceStatus
    amount_per_100g: Decimal | None


@dataclass(frozen=True)
class PurchaseCandidate:
    offer_id: str
    sku_id: str
    base_food_id: str
    food_name: str
    category: str
    merchant_id: str
    channel_id: str
    fulfilment_mode: str
    edible_grams_per_package: Decimal
    package_price: Decimal
    currency: str
    minimum_order: Decimal
    fulfilment_fee: Decimal
    free_delivery_threshold: Decimal | None
    nutrients: tuple[CandidateNutrient, ...]
    observed_at: datetime
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    def nutrient(self, measure: str) -> CandidateNutrient:
        for item in self.nutrients:
            if item.measure == measure:
                return item
        return CandidateNutrient(measure, EvidenceStatus.MISSING, None)


@dataclass(frozen=True)
class PlanningInputSnapshot:
    household_id: str
    as_of_date: date
    standard_version: str
    policy_version: str
    energy_target_kcal: Decimal
    targets: tuple[TargetDimension, ...]
    candidates: tuple[PurchaseCandidate, ...]


@dataclass(frozen=True)
class SolverLineDecision:
    offer_id: str
    package_count: int
    planned_grams: Decimal


@dataclass(frozen=True)
class SolverDecision:
    lines: tuple[SolverLineDecision, ...]
    status: str = "policy_optimal"


@dataclass(frozen=True)
class NutrientAssessment:
    measure: str
    indeterminate: bool
    amount: Decimal
    penalty: Decimal


@dataclass(frozen=True)
class PlanLine:
    offer_id: str
    sku_id: str
    base_food_id: str
    merchant_id: str
    channel_id: str
    package_count: int
    purchased_grams: Decimal
    planned_grams: Decimal
    surplus_grams: Decimal
    line_cost: Decimal


class PlanOutcome(StrEnum):
    MAPPED_COMPLETE = "mapped_complete"
    PARTIAL = "partial"
    NO_EXECUTABLE_PLAN = "no_executable_plan"


@dataclass(frozen=True)
class PurchasePlan:
    household_id: str
    as_of_date: date
    standard_version: str
    policy_version: str
    outcome: PlanOutcome
    lines: tuple[PlanLine, ...]
    total_cost: Decimal
    currency: str | None
    assessments: tuple[NutrientAssessment, ...]
    represented_categories: tuple[str, ...]
    represented_base_foods: tuple[str, ...]
    max_food_energy_share: Decimal
    provenance_offer_ids: tuple[str, ...]
