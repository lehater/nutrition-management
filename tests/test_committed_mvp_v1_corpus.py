from __future__ import annotations

import json
from pathlib import Path


_DATA = Path(__file__).resolve().parents[1] / "data" / "nutrition" / "mvp-v1"
_REQUIRED_ROW_KEYS = {
    "family_id",
    "row_id",
    "nutrient_measure",
    "source_semantic_kind",
    "target_kind",
    "basis",
    "source_unit",
    "lower",
    "upper",
    "point",
    "energy_kcal_per_g",
    "scope",
    "applicability",
    "source_id",
    "source_locator",
}


def test_committed_reference_shards_are_structurally_complete_and_uniquely_identified():
    files = sorted(_DATA.glob("references*.json"))
    assert files, "mvp-v1 reference corpus must contain committed shards"

    rows: list[dict] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert set(payload) == {"rows"}, path.name
        assert isinstance(payload["rows"], list) and payload["rows"], path.name
        for row in payload["rows"]:
            assert _REQUIRED_ROW_KEYS <= set(row), (path.name, row.get("row_id"))
            assert row["family_id"] and row["row_id"]
            assert row["source_id"] and row["source_locator"]
            assert isinstance(row["applicability"], dict)
        rows.extend(payload["rows"])

    row_ids = [row["row_id"] for row in rows]
    assert len(row_ids) == len(set(row_ids)), "row_id must be globally unique inside mvp-v1"

    active_families = {row["family_id"] for row in rows if row["scope"] == "active"}
    mappings = json.loads((_DATA / "mappings.json").read_text(encoding="utf-8"))["mappings"]
    mapping_families = [item["family_id"] for item in mappings]
    assert len(mapping_families) == len(set(mapping_families))
    assert set(mapping_families) == active_families
