from decimal import Decimal

import pytest

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.infrastructure.bls_v4_workbook import (
    BlsV4WorkbookStructureError,
    normalize_component_rows,
    normalize_food_rows,
)


COMPONENT_HEADER = (
    "Index",
    "Nährstoffcode / Component code",
    "Nährstoffbezeichnung",
    "Component name",
    "Einheit / Unit",
    "Nährstoffgruppe",
    "Component group",
    "Formeln / Formula",
    "Formelanwendung / Formula application",
)


def _component_rows():
    return [
        COMPONENT_HEADER,
        ("1", "ENERCC", "Energie", "Energy", "kcal", "Energie", "Energy", "", "immer berechnet"),
        ("2", "PROT625", "Protein", "Protein", "g", "Protein", "Protein", "", ""),
    ]


def _main_header():
    return (
        "BLS Code",
        "Lebensmittelbezeichnung",
        "Food name",
        "ENERCC Energie [kcal/100g]",
        "ENERCC Datenherkunft",
        "ENERCC Referenz",
        "PROT625 Protein [g/100g]",
        "PROT625 Datenherkunft",
        "PROT625 Referenz",
    )


def test_documented_component_and_main_triplet_structure_normalizes_source_evidence():
    components = normalize_component_rows(_component_rows(), expected_component_count=2)
    foods = normalize_food_rows(
        [
            _main_header(),
            (
                "A000001",
                "Testapfel",
                "Test apple",
                "52,3",
                "Analyse",
                "fixture-energy",
                "0",
                "Logische Null",
                "",
            ),
            (
                "B000001",
                "Testgetreide",
                "Test grain",
                "-",
                "",
                "",
                "<LOQ",
                "Analyse",
                "fixture-loq",
            ),
        ],
        components=components,
        category_by_code={
            "A000001": "fruit_and_vegetables",
            "B000001": "grains_cereal_products_potatoes",
        },
        expected_food_count=2,
    )

    apple, grain = foods
    assert apple.base_food_id == "bls:4.0:A000001"
    assert apple.nutrients[0].status == NutrientEvidenceStatus.KNOWN
    assert apple.nutrients[0].amount_per_100g == Decimal("52.3")
    assert apple.nutrients[0].source_value_text == "52,3"
    assert apple.nutrients[1].status == NutrientEvidenceStatus.ZERO
    assert apple.nutrients[1].amount_per_100g == Decimal(0)

    assert all(item.component_code != "ENERCC" for item in grain.nutrients)
    assert grain.nutrients[0].component_code == "PROT625"
    assert grain.nutrients[0].status == NutrientEvidenceStatus.BELOW_QUANTIFICATION_LIMIT
    assert grain.nutrients[0].amount_per_100g is None


def test_main_workbook_rejects_triplet_header_drift():
    components = normalize_component_rows(_component_rows(), expected_component_count=2)
    bad_header = list(_main_header())
    bad_header[5] = "PROT625 Referenz"

    with pytest.raises(BlsV4WorkbookStructureError, match="reference header"):
        normalize_food_rows(
            [tuple(bad_header)],
            components=components,
            category_by_code={},
            expected_food_count=0,
        )


def test_normalization_boundary_rejects_precoerced_numeric_cells():
    components = normalize_component_rows(_component_rows(), expected_component_count=2)

    with pytest.raises(BlsV4WorkbookStructureError, match="source-displayed text"):
        normalize_food_rows(
            [
                _main_header(),
                (
                    "A000001",
                    "Testapfel",
                    "Test apple",
                    52.3,
                    "Analyse",
                    "fixture-energy",
                    "0",
                    "Logische Null",
                    "",
                ),
            ],
            components=components,
            category_by_code={"A000001": "fruit_and_vegetables"},
            expected_food_count=1,
        )


def test_category_registry_must_cover_food_rows_exactly():
    components = normalize_component_rows(_component_rows(), expected_component_count=2)
    row = (
        "A000001",
        "Testapfel",
        "Test apple",
        "52,3",
        "Analyse",
        "fixture-energy",
        "0",
        "Logische Null",
        "",
    )

    with pytest.raises(BlsV4WorkbookStructureError, match="no explicit ADR-005 category mapping"):
        normalize_food_rows(
            [_main_header(), row],
            components=components,
            category_by_code={},
            expected_food_count=1,
        )
