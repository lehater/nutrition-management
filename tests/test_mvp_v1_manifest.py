from __future__ import annotations

from hashlib import sha256
import json

import pytest

from nutrition_management.nutrition_targeting.infrastructure.standard_data import (
    MVP_V1_DGE_TOPICS,
    StandardPackageError,
    compute_manifest_digest,
    load_standard_package,
)


def _canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_structural_mvp_v1(directory, *, break_topic: str | None = None) -> None:
    reference_topics = sorted(MVP_V1_DGE_TOPICS - {"energy", "alcohol"})
    rows = []
    mappings = []
    accounting = {
        "energy": {"status": "derived_policy", "policy_id": "dge-energy-mvp-v1"},
        "alcohol": {"status": "non_active", "reason": "DGE 2024 alcohol position replaced the former reference value"},
    }

    for topic in reference_topics:
        family_id = f"family-{topic}"
        rows.append(
            {
                "family_id": family_id,
                "row_id": f"row-{topic}",
                "nutrient_measure": topic,
                "source_semantic_kind": "estimated_value",
                "target_kind": "point",
                "basis": "absolute_daily",
                "source_unit": "mg",
                "lower": None,
                "upper": None,
                "point": "1",
                "energy_kcal_per_g": None,
                "scope": "active",
                "applicability": {},
                "source_id": "dge",
                "source_locator": f"fixture:{topic}",
            }
        )
        mappings.append(
            {
                "family_id": family_id,
                "status": "unsupported",
                "nutrient_measure": None,
                "canonical_unit": None,
                "formula_id": None,
                "reason": "structural manifest fixture",
            }
        )
        accounting[topic] = {"status": "reference_rows", "families": [family_id]}

    if break_topic is not None:
        accounting[break_topic] = {"status": "reference_rows", "families": [f"missing-{break_topic}"]}

    payloads = {
        "references.json": _canonical_bytes({"rows": rows}),
        "safety_limits.json": _canonical_bytes({"rows": []}),
        "mappings.json": _canonical_bytes({"mappings": mappings}),
    }
    for name, payload in payloads.items():
        (directory / name).write_bytes(payload)

    manifest = {
        "standard_version": "mvp-v1",
        "sources": [
            {
                "id": "dge",
                "name": "DGE/ÖGE Referenzwerte für die Nährstoffzufuhr",
                "version": "3rd edition, 1st issue 2025 + May 2026 erratum",
                "url": "https://www.dge.de/wissenschaft/referenzwerte/",
            }
        ],
        "topic_accounting": accounting,
        "files": {name: sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    manifest["package_digest"] = compute_manifest_digest(manifest)
    (directory / "manifest.json").write_bytes(_canonical_bytes(manifest))


def test_structurally_complete_mvp_v1_topic_accounting_loads(tmp_path):
    package_dir = tmp_path / "mvp-v1"
    package_dir.mkdir()
    _write_structural_mvp_v1(package_dir)

    package = load_standard_package(package_dir)
    assert package.standard.version == "mvp-v1"
    assert len(package.standard.mappings) == len(MVP_V1_DGE_TOPICS) - 2


def test_mvp_v1_topic_accounting_rejects_missing_or_phantom_active_family(tmp_path):
    package_dir = tmp_path / "mvp-v1"
    package_dir.mkdir()
    _write_structural_mvp_v1(package_dir, break_topic="vitamin_c")

    with pytest.raises(StandardPackageError, match="cover active reference families exactly"):
        load_standard_package(package_dir)
