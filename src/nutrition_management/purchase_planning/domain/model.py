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
class TargetCoverageGap:
    member_id: str
    family_id: str
    state: str
    missing_dimensions: tuple[str, ...] = ()
    candidate_reference_ids: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class MemberSafetyLimit:
    member_id: str
    reference_id: str
    measure: str
    daily_upper: Decimal


@dataclass(frozen=True)
class SafetyCoverageGap:
    member_id: str
    family_id: str
    state: str
    reason: str | None = None


@dataclass(frozen=True)
class TargetMemberProvenance:
    member_id: str
    age_years: int
    current_weight_kg: Decimal
    current_weight_date: date
    pal: Decimal
    pal_activity_adjustment_applied: bool


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
    derivation_date: date
    market_as_of: datetime
    standard_version: str
    policy_version: str
    energy_target_kcal: Decimal
    targets: tuple[TargetDimension, ...]
    candidates: tuple[PurchaseCandidate, ...]
    member_safety_limits: tuple[MemberSafetyLimit, ...] = ()
    target_member_provenance: tuple[TargetMemberProvenance, ...] = ()
    target_coverage_gaps: tuple[TargetCoverageGap, ...] = ()
    safety_coverage_gaps: tuple[SafetyCoverageGap, ...] = ()
    gap_suggestions: tuple[GapSuggestion, ...] = ()


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
    unknown_evidence: bool
    indeterminate: bool
    amount: Decimal
    penalty: Decimal


@dataclass(frozen=True)
class SafetyDiagnostic:
    measure: str
    planned_amount_30d: Decimal
    aggregate_period_equivalent_limit: Decimal
    exceeds_period_equivalent: bool
    indeterminate: bool
    allocation_guarantee: bool = False


@dataclass(frozen=True)
class TheoreticalFoodCandidate:
    base_food_id: str
    food_name: str
    category: str
    measure_amount_per_100g: Decimal
    energy_amount_per_100g: Decimal | None
    source_name: str
    source_version: str | None = None


@dataclass(frozen=True)
class GapSuggestion:
    measure: str
    base_food_id: str
    food_name: str
    category: str
    amount_per_100g: Decimal
    amount_per_100kcal: Decimal | None
    source_name: str
    source_version: str | None = None


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
    derivation_date: date
    market_as_of: datetime
    standard_version: str
    policy_version: str
    outcome: PlanOutcome
    lines: tuple[PlanLine, ...]
    total_cost: Decimal
    currency: str | None
    assessments: tuple[NutrientAssessment, ...]
    safety_diagnostics: tuple[SafetyDiagnostic, ...]
    represented_categories: tuple[str, ...]
    represented_base_foods: tuple[str, ...]
    max_food_energy_share: Decimal
    provenance_offer_ids: tuple[str, ...]
    target_member_provenance: tuple[TargetMemberProvenance, ...] = ()
    target_coverage_gaps: tuple[TargetCoverageGap, ...] = ()
    safety_coverage_gaps: tuple[SafetyCoverageGap, ...] = ()
