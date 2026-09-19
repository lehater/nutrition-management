from __future__ import annotations

import argparse
import json
from pathlib import Path

from nutrition_management.food_knowledge.infrastructure.bls_v4_source_codes import (
    extract_bls_v4_source_codes,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract the exact BLS 4.0 source-code set from the pinned main workbook"
    )
    parser.add_argument("workbook", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    payload = extract_bls_v4_source_codes(args.workbook)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(payload['source_codes'])} pinned BLS source codes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
