from nutrition_management.nutrition_targeting.domain.model import NutritionProfile, NutritionStandardSet


def import_profile(repository, household_id: str, profile: NutritionProfile) -> None:
    if not household_id:
        raise ValueError("household_id is required")
    repository.add_profile(household_id, profile)


def import_standard(repository, standard: NutritionStandardSet, *, active: bool) -> None:
    if not standard.version:
        raise ValueError("standard version is required")
    repository.add_standard(standard, active=active)
