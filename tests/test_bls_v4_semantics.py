from decimal import Decimal

import pytest

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.infrastructure.bls_v4_semantics import (
    BlsV4SemanticError,
    normalize_bls_value,
)


@pytest.mark.parametrize(
    ("raw_value", "origin", "status", "amount"),
    [
        ("52.3", "Analyse", NutrientEvidenceStatus.KNOWN, Decimal("52.3")),
        ("0", "Logische Null", NutrientEvidenceStatus.ZERO, Decimal(0)),
        ("0", "Rezeptberechnung", NutrientEvidenceStatus.ZERO, Decimal(0)),
        ("TR", "Spuren", NutrientEvidenceStatus.TRACE, None),
        ("<LOQ", "Analyse", NutrientEvidenceStatus.BELOW_QUANTIFICATION_LIMIT, None),
        ("<LOD", "Literatur", NutrientEvidenceStatus.BELOW_DETECTION_LIMIT, None),
        ("-", "-", NutrientEvidenceStatus.MISSING, None),
        (None, None, NutrientEvidenceStatus.MISSING, None),
    ],
)
def test_bls_value_normalization_preserves_source_evidence_semantics(
    raw_value, origin, status, amount
):
    assert normalize_bls_value(raw_value, origin) == (status, amount)


@pytest.mark.parametrize(
    ("raw_value", "origin", "error"),
    [
        ("1", "Unknown origin", "unsupported BLS data origin"),
        ("TR", "Analyse", "TR evidence must use data origin Spuren"),
        ("0", "Spuren", "Spuren must use the TR value marker"),
        ("1", "Logische Null", "Logische Null must contain numeric zero"),
        ("-1", "Analyse", "finite and non-negative"),
        ("-", "Analyse", "missing BLS value must not carry"),
        ("wat", "Analyse", "unsupported BLS value marker"),
    ],
)
def test_bls_value_normalization_fails_closed_on_inconsistent_source_semantics(
    raw_value, origin, error
):
    with pytest.raises(BlsV4SemanticError, match=error):
        normalize_bls_value(raw_value, origin)
