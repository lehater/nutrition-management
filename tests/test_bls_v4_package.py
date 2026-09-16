from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
import json

import pytest
from sqlalchemy import text

from nutrition_management.food_knowledge.application.contracts import NutrientEvidenceStatus
from nutrition_management.food_knowledge.infrastructure.bls_v4_data import (
    BlsV4PackageError,
    canonical_json,
    compute_manifest_digest,
    import_bls_v4_package,
    load_bls_v4_package,
)
from nutrition_management.food_knowledge.infrastructure.repository import FoodKnowledgeRepository


def _bytes(value) -> bytes:
    return (canonical_json(value) + "\n").encode("utf-8")


def _write_fixture_package(directory):
    directory.mkdir(parents=True, exist_ok=True)
    components = {
        "components": [
            {
                "component_code": "ENERCC",
                "name_de": "Energie",
                "name_en": "Energy",
                "unit": "kcal",
                "group_de": "Energie",
                "group_en": "Energy",
                "formula": None,
                "formula_application": "immer berechnet",
            },
            {
                "component_code": "PROT625",
                "name_de": "Protein",
                "name_en": "Protein",
                "unit": "g",
                "group_de": "Protein",
                "group_en": "Protein",
                "formula": None,
                "formula_application": None,
            },
        ]
    }
    categories = {
        "mappings": [
            {"source_code": "A000001", "category": "fruit_and_vegetables"},
            {"source_code": "B000001", "category": "grains_cereal_products_potatoes"},
        ]
    }
    foods = {
        "foods": [
            {
                "source_code": "A000001",
                "name_de": "Testapfel",
                "name_en": "Test apple",
                "nutrients": [
                    {
                        "component_code": "ENERCC",
                        "status": "known",
                        "amount_per_100g": "52.3",
                        "source_value_text": "52.3",
                        "value_origin": "Analyse",
                        "source_reference": "fixture-analysis",
                    },
                    {
                        "component_code": "PROT625",
                        "status": "zero",
                        "amount_per_100g": "0",
                        "source_value_text": "0",
                        "value_origin": "Logische Null",
                        "source_reference": None,
                    },
                ],
            },
            {
                "source_code": "B000001",
                "name_de": "Testgetreide",
                "name_en": "Test grain",
                "nutrients": [
                    {
                        "component_code": "PROT625",
                        "status": "trace",
                        "amount_per_100g": None,
                        "source_value_text": "0",
                        "value_origin": "Spuren",
                        "source_reference": "fixture-trace",
                    }
                ],
            },
        ]
    }
    payloads = {
        "components.json": _bytes(components),
        "category_mappings.json": _bytes(categories),
        "foods.0001.json": _bytes(foods),
    }
    for name, payload in payloads.items():
        (directory / name).write_bytes(payload)

    manifest = {
        "package_format": "bls-4.0-normalized-v1",
        "source": {
            "id": "bls-4.0",
            "name": "Bundeslebensmittelschluessel (BLS), Version 4.0",
            "version": "4.0",
            "doi": "10.25826/Data20251217-134202-0",
            "license": "CC BY 4.0",
            "url": "https://www.blsdb.de/download",
            "attribution": "Max Rubner-Institut (2025), BLS Version 4.0",
        },
        "source_files": {
            "BLS_4_0_Daten_2025_DE.xlsx": "1" * 64,
            "BLS_4_0_Components_DE_EN.xlsx": "2" * 64,
        },
        "files": {name: sha256(payload).hexdigest() for name, payload in payloads.items()},
        "food_files": ["foods.0001.json"],
        "food_count": 2,
        "component_count": 2,
    }
    manifest["package_digest"] = compute_manifest_digest(manifest)
    (directory / "manifest.json").write_bytes(_bytes(manifest))
    return directory


def test_bls_normalized_package_preserves_known_zero_trace_missing_and_categories(tmp_path):
    package_dir = _write_fixture_package(tmp_path / "bls-4.0")

    package = load_bls_v4_package(
        package_dir,
        expected_food_count=2,
        expected_component_count=2,
    )

    assert package.dataset.source_id == "bls-4.0"
    assert len(package.dataset.components) == 2
    assert [item.source_code for item in package.dataset.foods] == ["A000001", "B000001"]

    apple, grain = package.dataset.foods
    assert apple.base_food_id == "bls:4.0:A000001"
    assert apple.category == "fruit_and_vegetables"
    assert apple.nutrients[0].status == NutrientEvidenceStatus.KNOWN
    assert apple.nutrients[0].amount_per_100g == Decimal("52.3")
    assert apple.nutrients[1].status == NutrientEvidenceStatus.ZERO
    assert apple.nutrients[1].amount_per_100g == Decimal(0)
    assert grain.nutrients[0].status == NutrientEvidenceStatus.TRACE
    assert grain.nutrients[0].amount_per_100g is None
    assert all(item.component_code != "ENERCC" for item in grain.nutrients)


def test_bls_normalized_package_rejects_tampering_and_category_gaps(tmp_path):
    package_dir = _write_fixture_package(tmp_path / "bls-4.0")
    (package_dir / "foods.0001.json").write_text('{"foods":[]}\n', encoding="utf-8")

    with pytest.raises(BlsV4PackageError, match="digest mismatch"):
        load_bls_v4_package(package_dir, expected_food_count=2, expected_component_count=2)

    _write_fixture_package(package_dir)
    categories = json.loads((package_dir / "category_mappings.json").read_text(encoding="utf-8"))
    categories["mappings"].pop()
    category_bytes = _bytes(categories)
    (package_dir / "category_mappings.json").write_bytes(category_bytes)
    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest["files"]["category_mappings.json"] = sha256(category_bytes).hexdigest()
    manifest["package_digest"] = compute_manifest_digest(manifest)
    (package_dir / "manifest.json").write_bytes(_bytes(manifest))

    with pytest.raises(BlsV4PackageError, match="no explicit category mapping"):
        load_bls_v4_package(package_dir, expected_food_count=2, expected_component_count=2)


def test_bls_import_is_idempotent_and_persists_value_provenance(engine, tmp_path):
    package_dir = _write_fixture_package(tmp_path / "bls-4.0")
    package = load_bls_v4_package(
        package_dir,
        expected_food_count=2,
        expected_component_count=2,
    )

    with engine.begin() as connection:
        repository = FoodKnowledgeRepository(connection)
        assert import_bls_v4_package(repository, package) == "inserted"
        assert import_bls_v4_package(repository, package) == "unchanged"

        apple = repository.get_food("bls:4.0:A000001")
        assert apple.source_version == "4.0"
        assert apple.nutrient("PROT625").status == NutrientEvidenceStatus.ZERO

        provenance = connection.execute(
            text(
                "select source_value_text, value_origin, source_reference "
                "from fk_nutrient_value "
                "where base_food_id = :food_id and measure = :measure"
            ),
            {"food_id": "bls:4.0:A000001", "measure": "ENERCC"},
        ).mappings().one()
        assert provenance["source_value_text"] == "52.3"
        assert provenance["value_origin"] == "Analyse"
        assert provenance["source_reference"] == "fixture-analysis"

        component_count = connection.execute(
            text("select count(*) from fk_component where source_id = 'bls-4.0'")
        ).scalar_one()
        assert component_count == 2

        conflicting_digest = "f" * 64
        conflicting = replace(
            package,
            dataset=replace(package.dataset, package_digest=conflicting_digest),
            package_digest=conflicting_digest,
        )
        with pytest.raises(BlsV4PackageError, match="different content"):
            import_bls_v4_package(repository, conflicting)
