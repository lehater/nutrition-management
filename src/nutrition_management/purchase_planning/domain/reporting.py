from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from .model import (
    EvidenceStatus,
    NutrientAssessment,
    PlanLine,
    PlanOutcome,
    PlanningInputSnapshot,
    PurchasePlan,
    SolverDecision,
    TargetDimension,
    TargetKind,
)

CORE_CATEGORIES = {
    "fruit_and_vegetables",
    "legumes_nuts_seeds",
    "grains_cereal_products_potatoes",
    "oils_and_fats",
    "milk_and_dairy",
    "fish_meat_sausage_eggs",
}


def target_penalty(target: TargetDimension, amount: Decimal) -> Decimal:
    zero = Decimal(0)
    if target.kind in {TargetKind.ADEQUACY_FLOOR, TargetKind.LOWER_BOUND}:
        if target.lower is None or target.lower <= 0:
            raise ValueError("lower-bound target requires a positive lower value")
        return max(zero, (target.lower - amount) / target.lower)
    if target.kind == TargetKind.UPPER_BOUND:
        if target.upper is None or target.upper <= 0:
            raise ValueError("upper-bound target requires a positive upper value")
        return max(zero, (amount - target.upper) / target.upper)
    if target.kind == TargetKind.INTERVAL:
        if target.lower is None or target.upper is None or target.lower <= 0 or target.upper <= 0:
            raise ValueError("interval target requires positive lower/upper values")
        if amount < target.lower:
            return (target.lower - amount) / target.lower
        if amount > target.upper:
            return (amount - target.upper) / target.upper
        return zero
    if target.kind == TargetKind.POINT:
        if target.point is None or target.point <= 0:
            raise ValueError("point target requires a positive point value")
        lower = target.point * Decimal("0.95")
        upper = target.point * Decimal("1.05")
        if amount < lower:
            return (lower - amount) / lower
        if amount > upper:
            return (amount - upper) / upper
        return zero
    raise ValueError(f"unsupported target kind {target.kind}")


def _target_dimensions(snapshot: PlanningInputSnapshot) -> tuple[TargetDimension, ...]:
    energy = TargetDimension(measure="ENERCC", kind=TargetKind.POINT, point=snapshot.energy_target_kcal)
    return (energy, *snapshot.targets)


def build_purchase_plan(snapshot: PlanningInputSnapshot, decision: SolverDecision) -> PurchasePlan:
    candidates = {candidate.offer_id: candidate for candidate in snapshot.candidates}
    lines: list[PlanLine] = []
    planned_by_offer: dict[str, Decimal] = {}
    currency: str | None = None

    for chosen in decision.lines:
        candidate = candidates[chosen.offer_id]
        if chosen.package_count < 0 or chosen.planned_grams < 0:
            raise ValueError("solver returned negative decision quantity")
        purchased = candidate.edible_grams_per_package * chosen.package_count
        if chosen.planned_grams > purchased:
            raise ValueError("planned quantity exceeds purchased edible quantity")
        if chosen.package_count == 0 and chosen.planned_grams == 0:
            continue
        if currency is None:
            currency = candidate.currency
        elif candidate.currency != currency:
            raise ValueError("plan mixes currencies")
        planned_by_offer[chosen.offer_id] = chosen.planned_grams
        lines.append(
            PlanLine(
                offer_id=candidate.offer_id,
                sku_id=candidate.sku_id,
                base_food_id=candidate.base_food_id,
                merchant_id=candidate.merchant_id,
                channel_id=candidate.channel_id,
                package_count=chosen.package_count,
                purchased_grams=purchased,
                planned_grams=chosen.planned_grams,
                surplus_grams=purchased - chosen.planned_grams,
                line_cost=candidate.package_price * chosen.package_count,
            )
        )

    channel_subtotals: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
    for line in lines:
        channel_subtotals[line.channel_id] += line.line_cost
    total_cost = sum((line.line_cost for line in lines), Decimal(0))
    for channel_id, subtotal in channel_subtotals.items():
        sample = next(candidate for candidate in snapshot.candidates if candidate.channel_id == channel_id)
        if subtotal < sample.minimum_order:
            raise ValueError("solver returned group below minimum order")
        if sample.fulfilment_fee > 0:
            if sample.free_delivery_threshold is None or subtotal < sample.free_delivery_threshold:
                total_cost += sample.fulfilment_fee

    assessments: list[NutrientAssessment] = []
    for target in _target_dimensions(snapshot):
        amount = Decimal(0)
        indeterminate = False
        for offer_id, grams in planned_by_offer.items():
            if grams <= 0:
                continue
            evidence = candidates[offer_id].nutrient(target.measure)
            if evidence.status in {EvidenceStatus.TRACE, EvidenceStatus.MISSING}:
                indeterminate = True
            elif evidence.amount_per_100g is not None:
                amount += evidence.amount_per_100g * grams / Decimal(100)
        assessments.append(
            NutrientAssessment(
                measure=target.measure,
                indeterminate=indeterminate,
                amount=amount,
                penalty=target_penalty(target, amount),
            )
        )

    total_mass = sum(planned_by_offer.values(), Decimal(0))
    energy_by_food: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
    mass_by_food: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
    category_by_food: dict[str, str] = {}
    for offer_id, grams in planned_by_offer.items():
        candidate = candidates[offer_id]
        mass_by_food[candidate.base_food_id] += grams
        category_by_food[candidate.base_food_id] = candidate.category
        energy = candidate.nutrient("ENERCC")
        if energy.amount_per_100g is not None:
            energy_by_food[candidate.base_food_id] += energy.amount_per_100g * grams / Decimal(100)
    total_energy = sum(energy_by_food.values(), Decimal(0))

    represented_foods: list[str] = []
    for food_id in sorted(mass_by_food):
        mass_share = Decimal(0) if total_mass == 0 else mass_by_food[food_id] / total_mass
        energy_share = Decimal(0) if total_energy == 0 else energy_by_food[food_id] / total_energy
        if mass_share >= Decimal("0.01") or energy_share >= Decimal("0.01"):
            represented_foods.append(food_id)
    represented_categories = sorted({category_by_food[food_id] for food_id in represented_foods})
    max_share = Decimal(0)
    if total_energy > 0 and energy_by_food:
        max_share = max((value / total_energy for value in energy_by_food.values()), default=Decimal(0))

    nutrition_ok = all(not item.indeterminate and item.penalty == 0 for item in assessments)
    core_count = len(set(represented_categories) & CORE_CATEGORIES)
    variety_ok = core_count >= 4 and len(represented_foods) >= 8 and max_share <= Decimal("0.25")
    outcome = PlanOutcome.MAPPED_COMPLETE if nutrition_ok and variety_ok else PlanOutcome.PARTIAL

    return PurchasePlan(
        household_id=snapshot.household_id,
        derivation_date=snapshot.derivation_date,
        market_as_of=snapshot.market_as_of,
        standard_version=snapshot.standard_version,
        policy_version=snapshot.policy_version,
        outcome=outcome,
        lines=tuple(sorted(lines, key=lambda item: item.offer_id)),
        total_cost=total_cost,
        currency=currency,
        assessments=tuple(assessments),
        represented_categories=tuple(represented_categories),
        represented_base_foods=tuple(represented_foods),
        max_food_energy_share=max_share,
        provenance_offer_ids=tuple(sorted(planned_by_offer)),
    )
