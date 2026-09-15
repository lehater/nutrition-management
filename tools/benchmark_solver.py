from __future__ import annotations

import argparse
from datetime import UTC, date, datetime
from decimal import Decimal
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pyscipopt

from nutrition_management.purchase_planning.domain.model import (
    CandidateNutrient,
    EvidenceStatus,
    PlanningInputSnapshot,
    PurchaseCandidate,
    TargetDimension,
    TargetKind,
)
from nutrition_management.purchase_planning.infrastructure import scip_solver

NOW = datetime(2026, 9, 15, 12, tzinfo=UTC)
CORE_CATEGORIES = (
    "fruit_and_vegetables",
    "legumes_nuts_seeds",
    "grains_cereal_products_potatoes",
    "oils_and_fats",
    "milk_and_dairy",
    "fish_meat_sausage_eggs",
)


def _nutrient(measure: str, value: str) -> CandidateNutrient:
    return CandidateNutrient(measure, EvidenceStatus.KNOWN, Decimal(value))


def synthetic_snapshot(offer_count: int) -> PlanningInputSnapshot:
    candidates = []
    for index in range(offer_count):
        category = CORE_CATEGORIES[index % len(CORE_CATEGORIES)]
        merchant = f"merchant-{index % 4}"
        channel = f"channel-{index % 4}"
        candidates.append(
            PurchaseCandidate(
                offer_id=f"offer-{index:03d}",
                sku_id=f"sku-{index:03d}",
                base_food_id=f"food-{index:03d}",
                food_name=f"Synthetic Food {index}",
                category=category,
                merchant_id=merchant,
                channel_id=channel,
                fulfilment_mode="pickup",
                edible_grams_per_package=Decimal("1000"),
                package_price=Decimal("2.00") + Decimal(index % 7) / Decimal("10"),
                currency="EUR",
                minimum_order=Decimal(0),
                fulfilment_fee=Decimal(0),
                free_delivery_threshold=None,
                nutrients=(
                    _nutrient("ENERCC", str(160 + (index % 5) * 20)),
                    _nutrient("PROT625", str(8 + (index % 4))),
                    _nutrient("FIBT", str(2 + (index % 3))),
                    _nutrient("CHO", str(18 + (index % 5) * 2)),
                    _nutrient("NACL", "0.2"),
                ),
                observed_at=NOW,
            )
        )

    return PlanningInputSnapshot(
        household_id="synthetic-household",
        derivation_date=date(2026, 9, 15),
        market_as_of=NOW,
        standard_version="benchmark-fixture-v1",
        policy_version="ADR-007-v1",
        energy_target_kcal=Decimal("60000"),
        targets=(
            TargetDimension("PROT625", TargetKind.ADEQUACY_FLOOR, lower=Decimal("3000")),
            TargetDimension("FIBT", TargetKind.ADEQUACY_FLOOR, lower=Decimal("1500")),
            TargetDimension("CHO", TargetKind.INTERVAL, lower=Decimal("6750"), upper=Decimal("8250")),
            TargetDimension("NACL", TargetKind.UPPER_BOUND, upper=Decimal("360")),
        ),
        candidates=tuple(candidates),
    )


def run_case(offer_count: int) -> dict:
    snapshot = synthetic_snapshot(offer_count)
    original = scip_solver._optimize_stage
    stages: list[dict] = []

    def traced(model, expression, *, sense, name, allow_initial_infeasible=False, fix=True):
        started = perf_counter()
        try:
            result = original(
                model,
                expression,
                sense=sense,
                name=name,
                allow_initial_infeasible=allow_initial_infeasible,
                fix=fix,
            )
        finally:
            stages.append(
                {
                    "name": name,
                    "sense": sense,
                    "status": str(model.getStatus()).lower(),
                    "wall_seconds": round(perf_counter() - started, 6),
                    "variables": model.getNVars(),
                    "constraints": model.getNConss(),
                }
            )
        return result

    scip_solver._optimize_stage = traced
    started = perf_counter()
    try:
        decision = scip_solver.solve(snapshot)
    finally:
        scip_solver._optimize_stage = original
    total = perf_counter() - started

    return {
        "offers": offer_count,
        "base_foods": offer_count,
        "mapped_target_dimensions": 5,
        "stage_count": len(stages),
        "max_variables": max((stage["variables"] for stage in stages), default=0),
        "max_constraints": max((stage["constraints"] for stage in stages), default=0),
        "total_wall_seconds": round(total, 6),
        "final_status": decision.status,
        "selected_lines": len(decision.lines),
        "stages": stages,
    }


def runtime_environment() -> dict:
    model = pyscipopt.Model()
    try:
        scip = f"{model.getMajorVersion()}.{model.getMinorVersion()}.{model.getTechVersion()}"
    finally:
        model.freeProb()
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "logical_cpu_count": os.cpu_count(),
        "runner_os": os.getenv("RUNNER_OS"),
        "runner_arch": os.getenv("RUNNER_ARCH"),
        "pyscipopt": pyscipopt.__version__,
        "scip": scip,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = {
        "benchmark": "first-implementation-slice",
        "environment": runtime_environment(),
        "cases": [run_case(16), run_case(32)],
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
