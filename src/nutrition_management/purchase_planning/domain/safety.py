from collections import defaultdict
from decimal import Decimal

from .model import PlanningInputSnapshot, SafetyDiagnostic

_DAYS = Decimal(30)


def build_safety_diagnostics(snapshot: PlanningInputSnapshot, planned_by_offer: dict[str, Decimal]):
    candidates = {item.offer_id: item for item in snapshot.candidates}
    limits_by_measure = defaultdict(list)
    for limit in snapshot.member_safety_limits:
        limits_by_measure[limit.measure].append(limit)

    diagnostics = []
    for measure, limits in sorted(limits_by_measure.items()):
        known_planned_amount = Decimal(0)
        indeterminate = False
        for offer_id, grams in planned_by_offer.items():
            if grams <= 0:
                continue
            evidence = candidates[offer_id].nutrient(measure)
            if not evidence.status.is_quantitatively_known:
                indeterminate = True
            elif evidence.amount_per_100g is not None:
                known_planned_amount += evidence.amount_per_100g * grams / Decimal(100)
        period_equivalent = sum((item.daily_upper * _DAYS for item in limits), Decimal(0))
        diagnostics.append(
            SafetyDiagnostic(
                measure=measure,
                planned_amount_30d=known_planned_amount,
                aggregate_period_equivalent_limit=period_equivalent,
                # Unknown contributions are non-negative. They prevent proving the
                # exact total or proving non-exceedance, but cannot invalidate an
                # exceedance already proved by the known lower-bound contribution.
                exceeds_period_equivalent=known_planned_amount > period_equivalent,
                indeterminate=indeterminate,
                allocation_guarantee=False,
            )
        )
    return tuple(diagnostics)
