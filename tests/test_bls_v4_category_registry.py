import pytest

from nutrition_management.food_knowledge.domain.model import TOP_LEVEL_CATEGORIES
from nutrition_management.food_knowledge.application.category_registry import (
    CategoryRegistryError,
    validate_category_registry,
)


def source(*codes):
    return {"source_version": "4.0", "source_codes": list(codes)}


def registry(*pairs):
    return {
        "source_version": "4.0",
        "mappings": [
            {"source_code": code, "category": category}
            for code, category in pairs
        ],
    }


def test_category_registry_requires_exact_sorted_coverage():
    validate_category_registry(
        source("A000001", "C131000"),
        registry(
            ("A000001", "fruit_and_vegetables"),
            ("C131000", "grains_cereal_products_potatoes"),
        ),
        expected_count=2,
    )


@pytest.mark.parametrize(
    ("value", "error"),
    [
        (
            registry(("A000001", "fruit_and_vegetables")),
            "cover source codes exactly",
        ),
        (
            registry(
                ("A000001", "fruit_and_vegetables"),
                ("B000001", "other_or_composite"),
                ("C131000", "grains_cereal_products_potatoes"),
            ),
            "cover source codes exactly",
        ),
        (
            registry(
                ("C131000", "grains_cereal_products_potatoes"),
                ("A000001", "fruit_and_vegetables"),
            ),
            "sorted by source_code",
        ),
    ],
)
def test_category_registry_rejects_missing_extra_or_nondeterministic_order(value, error):
    with pytest.raises(CategoryRegistryError, match=error):
        validate_category_registry(
            source("A000001", "C131000"),
            value,
            expected_count=2,
        )


def test_category_registry_rejects_duplicate_mapping():
    value = registry(
        ("A000001", "fruit_and_vegetables"),
        ("A000001", "other_or_composite"),
    )
    with pytest.raises(CategoryRegistryError, match="duplicate category mapping"):
        validate_category_registry(
            source("A000001", "C131000"),
            value,
            expected_count=2,
        )


def test_category_registry_rejects_unknown_category():
    assert "store_aisle_42" not in TOP_LEVEL_CATEGORIES
    with pytest.raises(CategoryRegistryError, match="ADR-005 top-level category"):
        validate_category_registry(
            source("A000001"),
            registry(("A000001", "store_aisle_42")),
            expected_count=1,
        )


def test_category_registry_is_version_scoped():
    value = registry(("A000001", "fruit_and_vegetables"))
    value["source_version"] = "5.0"
    with pytest.raises(CategoryRegistryError, match="registry source_version"):
        validate_category_registry(
            source("A000001"),
            value,
            expected_count=1,
        )


def test_source_code_baseline_must_be_unique_and_complete():
    with pytest.raises(CategoryRegistryError, match="source_codes must be unique"):
        validate_category_registry(
            source("A000001", "A000001"),
            registry(("A000001", "fruit_and_vegetables")),
            expected_count=2,
        )
