from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class TargetFact:
    measure: str
    kind: str
    lower_30d: Decimal | None
    upper_30d: Decimal | None
    point_30d: Decimal | None


@dataclass(frozen=True)
class TargetCoverageFact:
    member_id: str
    family_id: str
    state: str
    missing_dimensions: tuple[str, ...] = ()
    candidate_reference_ids: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class MemberSafetyFact:
    member_id: str
    reference_id: str
    measure: str
    daily_upper: Decimal


@dataclass(frozen=True)
class SafetyCoverageFact:
    member_id: str
    family_id: str
    state: str
    reason: str | None = None


@dataclass(frozen=True)
class MemberTargetProvenanceFact:
    member_id: str
    age_years: int
    current_weight_kg: Decimal
    current_weight_date: date
    pal: Decimal
    pal_activity_adjustment_applied: bool


@dataclass(frozen=True)
class HouseholdTargetFact:
    household_id: str
    derivation_date: date
    standard_version: str
    energy_kcal_30d: Decimal
    targets: tuple[TargetFact, ...]
    member_ids: tuple[str, ...]
    member_safety_limits: tuple[MemberSafetyFact, ...]
    member_provenance: tuple[MemberTargetProvenanceFact, ...]
    target_coverage_gaps: tuple[TargetCoverageFact, ...] = ()
    safety_coverage_gaps: tuple[SafetyCoverageFact, ...] = ()
