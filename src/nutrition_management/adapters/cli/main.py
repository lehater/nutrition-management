from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import json

from nutrition_management.composition.database import create_sqlite_engine
from nutrition_management.composition.planning_snapshot import PlanningSnapshotSource
from nutrition_management.purchase_planning.application.service import generate_purchase_plan
from nutrition_management.purchase_planning.infrastructure.solver_adapter import solve


def _json_default(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"cannot JSON encode {type(value)!r}")


def canonical_plan_json(plan) -> str:
    return json.dumps(asdict(plan), default=_json_default, sort_keys=True, separators=(",", ":"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="nutrition-plan")
    parser.add_argument("--db", required=True)
    parser.add_argument("--household", required=True)
    parser.add_argument("--derivation-date", required=True)
    parser.add_argument("--market-as-of", required=True)
    args = parser.parse_args(argv)

    derivation_date = date.fromisoformat(args.derivation_date)
    market_as_of = datetime.fromisoformat(args.market_as_of)
    engine = create_sqlite_engine(args.db)
    try:
        plan = generate_purchase_plan(
            snapshot_source=PlanningSnapshotSource(engine),
            solver=solve,
            household_id=args.household,
            derivation_date=derivation_date,
            market_as_of=market_as_of,
        )
        print(canonical_plan_json(plan))
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
