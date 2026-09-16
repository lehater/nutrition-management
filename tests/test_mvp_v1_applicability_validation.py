from decimal import Decimal

import pytest

from nutrition_management.nutrition_targeting.domain.model import (
    AgeBoundary,
    AgeUnit,
    ApplicabilityRequirement,
    ReferenceApplicability,
    ReferenceBasis,
    ReferenceDefinition,
    ReferenceKind,
)
from nutrition_management.nutrition_targeting.infrastructure.mvp_v1_standard_data import (
    _validate_deterministic_families,
)
from nutrition_management.nutrition_targeting.infrastructure.standard_data import StandardPackageError


def _row(reference_id: str, applicability: ReferenceApplicability) -> ReferenceDefinition:
    return ReferenceDefinition(
        reference_id=reference_id,
        family_id="family",
        nutrient_measure="measure",
        kind=ReferenceKind.ADEQUACY_FLOOR,
        basis=ReferenceBasis.ABSOLUTE_DAILY,
        lower=Decimal("1"),
        source_unit="mg",
        applicability=applicability,
    )


def test_production_validation_rejects_overlapping_generic_and_conditional_rows():
    adult = ReferenceApplicability(min_age=AgeBoundary(19, AgeUnit.YEARS))
    conditional = ReferenceApplicability(
        min_age=AgeBoundary(19, AgeUnit.YEARS),
        requirements=(ApplicabilityRequirement("status", "a"),),
    )

    with pytest.raises(StandardPackageError, match="ambiguous active source variants"):
        _validate_deterministic_families((_row("generic", adult), _row("conditional", conditional)), label="reference")


def test_production_validation_accepts_disjoint_requirement_variants_and_calendar_age_bands():
    status_a = ReferenceApplicability(
        min_age=AgeBoundary(19, AgeUnit.YEARS),
        requirements=(ApplicabilityRequirement("status", "a"),),
    )
    status_b = ReferenceApplicability(
        min_age=AgeBoundary(19, AgeUnit.YEARS),
        requirements=(ApplicabilityRequirement("status", "b"),),
    )
    infant = ReferenceApplicability(
        min_age=AgeBoundary(4, AgeUnit.MONTHS),
        max_age=AgeBoundary(12, AgeUnit.MONTHS),
    )
    child = ReferenceApplicability(
        min_age=AgeBoundary(1, AgeUnit.YEARS),
        max_age=AgeBoundary(4, AgeUnit.YEARS),
    )

    _validate_deterministic_families((_row("status-a", status_a), _row("status-b", status_b)), label="reference")
    _validate_deterministic_families((_row("infant", infant), _row("child", child)), label="reference")
