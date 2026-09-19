from __future__ import annotations

from typing import Protocol

from nutrition_management.nutrition_targeting.domain.model import (
    NutritionProfile,
    NutritionStandardSet,
)


class TargetDerivationSource(Protocol):
    def profiles_for_household(self, household_id: str) -> tuple[NutritionProfile, ...]: ...

    def active_standard(self) -> NutritionStandardSet: ...


class ProfileSink(Protocol):
    def add_profile(self, household_id: str, profile: NutritionProfile) -> None: ...


class StandardSink(Protocol):
    def add_standard(
        self,
        standard: NutritionStandardSet,
        *,
        active: bool = False,
    ) -> None: ...
