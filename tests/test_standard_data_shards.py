from __future__ import annotations

from hashlib import sha256
import json

from nutrition_management.nutrition_targeting.infrastructure.standard_data import compute_manifest_digest, load_standard_package


def _canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _row(family_id: str, row_id: str) -> dict:
    return {
        "family_id": family_id,
        "row_id": row_id,
        "nutrient_measure": family_id,
        "source_semantic_kind": "estimated_value",
        "target_kind": "adequacy_floor",
        "basis": "absolute_daily",
        "source_unit": "mg",
        "lower": "1",
        "upper": None,
        "point": None,
        "energy_kcal_per_g": None,
        "scope": "active",
        "applicability": {},
        "source_id": "source",
        "source_locator": row_id,
    }


def test_reference_shards_are_digest_tracked_and_loaded_as_one_standard(tmp_path):
    package_dir = tmp_path / "package"
    package_dir.mkdir()

    payloads = {
        "references.json": _canonical_bytes({"rows": [_row("base-family", "base-row")]}),
        "references.vitamins.json": _canonical_bytes({"rows": [_row("vitamin-family", "vitamin-row")]}),
        "safety_limits.json": _canonical_bytes({"rows": []}),
        "mappings.json": _canonical_bytes(
            {
                "mappings": [
                    {
                        "family_id": family_id,
                        "status": "unsupported",
                        "nutrient_measure": None,
                        "canonical_unit": None,
                        "formula_id": None,
                        "reason": "test",
                    }
                    for family_id in ("base-family", "vitamin-family")
                ]
            }
        ),
    }
    for name, payload in payloads.items():
        (package_dir / name).write_bytes(payload)

    manifest = {
        "standard_version": "sharded-v1",
        "sources": [{"id": "source", "name": "test", "version": "1", "url": "https://example.invalid/source"}],
        "reference_files": ["references.json", "references.vitamins.json"],
        "files": {name: sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    manifest["package_digest"] = compute_manifest_digest(manifest)
    (package_dir / "manifest.json").write_bytes(_canonical_bytes(manifest))

    package = load_standard_package(package_dir)
    assert [item.reference_id for item in package.standard.references] == ["base-row", "vitamin-row"]
    assert package.standard.content_digest == manifest["package_digest"]
