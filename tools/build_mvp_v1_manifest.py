from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "nutrition" / "mvp-v1"

TOPIC_FAMILIES = {
    "protein": ["dge.protein"],
    "fat_and_essential_fatty_acids": [
        "dge.total_fat",
        "dge.linoleic_acid",
        "dge.alpha_linolenic_acid",
        "dge.saturated_fat",
        "dge.mufa",
        "dge.pufa",
        "dge.epa_dha",
        "dge.trans_fat",
    ],
    "carbohydrates": ["dge.carbohydrates"],
    "fibre": ["dge.fibre"],
    "water": ["dge.water_total"],
    "vitamin_a": ["dge.vitamin_a"],
    "vitamin_d": ["dge.vitamin_d"],
    "vitamin_e": ["dge.vitamin_e"],
    "vitamin_k": ["dge.vitamin_k"],
    "thiamin": ["dge.thiamin"],
    "riboflavin": ["dge.riboflavin"],
    "niacin": ["dge.niacin"],
    "vitamin_b6": ["dge.vitamin_b6"],
    "folate": ["dge.folate"],
    "pantothenic_acid": ["dge.pantothenic_acid"],
    "biotin": ["dge.biotin"],
    "vitamin_b12": ["dge.vitamin_b12"],
    "vitamin_c": ["dge.vitamin_c"],
    "sodium": ["dge.sodium"],
    "chloride": ["dge.chloride"],
    "potassium": ["dge.potassium"],
    "calcium": ["dge.calcium"],
    "phosphorus": ["dge.phosphorus"],
    "magnesium": ["dge.magnesium"],
    "iron": ["dge.iron"],
    "iodine": ["dge.iodine"],
    "fluoride": ["dge.fluoride"],
    "zinc": ["dge.zinc"],
    "selenium": ["dge.selenium"],
    "copper": ["dge.copper"],
    "chromium": ["dge.chromium"],
    "manganese": ["dge.manganese"],
    "molybdenum": ["dge.molybdenum"],
}


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_rows(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
            raise ValueError(f"{path.name}: expected object with rows array")
        rows.extend(payload["rows"])
    return rows


def source_entry(source_id: str) -> dict:
    if source_id.startswith("dge-"):
        return {
            "id": source_id,
            "name": f"DGE/OEGE reference values: {source_id.removeprefix('dge-')}",
            "version": "3rd edition, 1st issue 2025; May 2026 erratum",
            "url": "https://www.dge.de/wissenschaft/referenzwerte/",
        }
    if source_id == "efsa-ul-overview-v11":
        return {
            "id": source_id,
            "name": "EFSA Overview on Tolerable Upper Intake Levels",
            "version": "Version 11, August 2025",
            "url": "https://www.efsa.europa.eu/sites/default/files/2024-05/ul-summary-report.pdf",
        }
    raise ValueError(f"unknown source id: {source_id}")


def build_manifest() -> dict:
    reference_paths = sorted(DATA.glob("references*.json"), key=lambda path: path.name)
    if not reference_paths or reference_paths[0].name != "references.json":
        # Lexical ordering can put a shard before the base file; enforce membership instead.
        if not any(path.name == "references.json" for path in reference_paths):
            raise ValueError("references.json is required")
    reference_paths = [DATA / "references.json", *[p for p in reference_paths if p.name != "references.json"]]
    required = [DATA / "mappings.json", DATA / "safety_limits.json"]
    for path in [*reference_paths, *required]:
        if not path.is_file():
            raise ValueError(f"missing corpus file: {path.name}")

    reference_rows = load_rows(reference_paths)
    safety_rows = load_rows([DATA / "safety_limits.json"])
    active_families = {
        row["family_id"]
        for row in reference_rows
        if row.get("scope", "active") == "active"
    }
    expected_families = {family for families in TOPIC_FAMILIES.values() for family in families}
    if active_families != expected_families:
        raise ValueError(
            f"topic family mismatch; missing={sorted(expected_families-active_families)}, "
            f"extra={sorted(active_families-expected_families)}"
        )

    source_ids = sorted(
        {row["source_id"] for row in [*reference_rows, *safety_rows]}
    )
    sources = [source_entry(source_id) for source_id in source_ids]

    topic_accounting = {
        "energy": {"status": "derived_policy", "policy_id": "ADR-003-adult-energy"},
        "alcohol": {
            "status": "non_active",
            "reason": "The 2024 DGE alcohol position replaced the former numeric reference value; mvp-v1 does not resurrect a legacy alcohol target.",
        },
    }
    topic_accounting.update(
        {
            topic: {"status": "reference_rows", "families": families}
            for topic, families in TOPIC_FAMILIES.items()
        }
    )

    file_paths = [*reference_paths, DATA / "safety_limits.json", DATA / "mappings.json"]
    files = {path.name: file_sha256(path) for path in sorted(file_paths, key=lambda p: p.name)}
    manifest = {
        "standard_version": "mvp-v1",
        "edition": "DGE/OEGE 3rd edition, 1st issue 2025",
        "correction": "May 2026 erratum",
        "sources": sources,
        "reference_files": [path.name for path in reference_paths],
        "files": files,
        "topic_accounting": topic_accounting,
    }
    manifest["package_digest"] = sha256(canonical_json(manifest).encode("utf-8")).hexdigest()
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = canonical_json(build_manifest()) + "\n"
    if args.write is not None:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(content, encoding="utf-8")
    if args.check:
        path = DATA / "manifest.json"
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise SystemExit("data/nutrition/mvp-v1/manifest.json is not reproducible; run this tool with --write")
    if args.write is None and not args.check:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
