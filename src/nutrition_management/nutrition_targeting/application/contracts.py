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
class HouseholdTargetFact:
    household_id: str
    derivation_date: date
    standard_version: str
    energy_kcal_30d: Decimal
    targets: tuple[TargetFact, ...]
    member_ids: tuple[str, ...]
