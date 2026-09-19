import pytest

from nutrition_management.food_knowledge.application.category_registry import (
    CategoryRegistryError,
    resolve_category_registry,
    validate_category_registry,
)
from nutrition_management.food_knowledge.domain.model import TOP_LEVEL_CATEGORIES


def source(*codes):
    return {"source_version": "4.0", "source_codes": list(codes)}


def registry(*rules, overrides=()):
    return {
        "source_version": "4.0",
        "rules": [
            {"prefix": prefix, "category": category}
            for prefix, category in rules
        ],
        "overrides": [
            {"source_code": code, "category": category}
            for code, category in overrides
        ],
    }


def test_category_registry_resolves_prefix_rules_and_exact_override():
    value = registry(
        ("B", "grains_cereal_products_potatoes"),
        ("F", "fruit_and_vegetables"),
        overrides=(("B999999", "other_or_composite"),),
    )
    resolved = resolve_category_registry(
        source("B111000", "B999999", "F110100"),
        value,
        expected_count=3,
    )
    assert resolved == {
        "B111000": "grains_cereal_products_potatoes",
        "B999999": "other_or_composite",
        "F110100": "fruit_and_vegetables",
    }


def test_category_registry_rejects_unmapped_source_code():
    with pytest.raises(CategoryRegistryError, match="no category decision"):
        validate_category_registry(
            source("B111000", "F110100"),
            registry(("B", "grains_cereal_products_potatoes")),
            expected_count=2,
        )


def test_category_registry_rejects_ambiguous_prefix_rules():
    with pytest.raises(CategoryRegistryError, match="multiple prefix rules"):
        validate_category_registry(
            source("E410000"),
            registry(
                ("E", "other_or_composite"),
                ("E4", "grains_cereal_products_potatoes"),
            ),
            expected_count=1,
        )


def test_exact_override_may_resolve_a_code_inside_a_broader_rule():
    validate_category_registry(
        source("E110000", "E410000"),
        registry(
            ("E", "fish_meat_sausage_eggs"),
            overrides=(("E410000", "grains_cereal_products_potatoes"),),
        ),
        expected_count=2,
    )


def test_category_registry_rejects_unknown_override_code():
    with pytest.raises(CategoryRegistryError, match="not in the pinned source set"):
        validate_category_registry(
            source("B111000"),
            registry(
                ("B", "grains_cereal_products_potatoes"),
                overrides=(("F110100", "fruit_and_vegetables"),),
            ),
            expected_count=1,
        )


def test_category_registry_rejects_unused_rule():
    with pytest.raises(CategoryRegistryError, match="match no non-overridden source codes"):
        validate_category_registry(
            source("B111000"),
            registry(
                ("B", "grains_cereal_products_potatoes"),
                ("F", "fruit_and_vegetables"),
            ),
            expected_count=1,
        )


def test_category_registry_rejects_duplicate_prefix_rule():
    with pytest.raises(CategoryRegistryError, match="duplicate prefix rule"):
        validate_category_registry(
            source("B111000"),
            registry(
                ("B", "grains_cereal_products_potatoes"),
                ("B", "other_or_composite"),
            ),
            expected_count=1,
        )


def test_category_registry_requires_deterministic_rule_and_override_order():
    with pytest.raises(CategoryRegistryError, match="rules must be sorted"):
        validate_category_registry(
            source("B111000", "F110100"),
            registry(
                ("F", "fruit_and_vegetables"),
                ("B", "grains_cereal_products_potatoes"),
            ),
            expected_count=2,
        )

    with pytest.raises(CategoryRegistryError, match="overrides must be sorted"):
        validate_category_registry(
            source("B111000", "B999999", "F110100"),
            registry(
                ("B", "grains_cereal_products_potatoes"),
                ("F", "fruit_and_vegetables"),
                overrides=(
                    ("F110100", "other_or_composite"),
                    ("B999999", "other_or_composite"),
                ),
            ),
            expected_count=3,
        )


def test_category_registry_rejects_unknown_category():
    assert "store_aisle_42" not in TOP_LEVEL_CATEGORIES
    with pytest.raises(CategoryRegistryError, match="ADR-005 top-level category"):
        validate_category_registry(
            source("B111000"),
            registry(("B", "store_aisle_42")),
            expected_count=1,
        )


def test_category_registry_is_version_scoped():
    value = registry(("B", "grains_cereal_products_potatoes"))
    value["source_version"] = "5.0"
    with pytest.raises(CategoryRegistryError, match="registry source_version"):
        validate_category_registry(
            source("B111000"),
            value,
            expected_count=1,
        )


def test_source_code_baseline_must_be_unique_and_complete():
    with pytest.raises(CategoryRegistryError, match="source_codes must be unique"):
        validate_category_registry(
            source("B111000", "B111000"),
            registry(("B", "grains_cereal_products_potatoes")),
            expected_count=2,
        )
