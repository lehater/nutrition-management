from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from pyscipopt import Model, quicksum

from nutrition_management.purchase_planning.domain.model import (
    EvidenceStatus,
    PlanningInputSnapshot,
    SolverDecision,
    SolverLineDecision,
    TargetDimension,
    TargetKind,
)

_EPS = 1e-8
_CORE_CATEGORIES = {
    "fruit_and_vegetables",
    "legumes_nuts_seeds",
    "grains_cereal_products_potatoes",
    "oils_and_fats",
    "milk_and_dairy",
    "fish_meat_sausage_eggs",
}


class SolverTechnicalFailure(RuntimeError):
    pass


class HardModelInfeasible(RuntimeError):
    pass


@dataclass
class _Vars:
    packages: dict[str, object]
    planned: dict[str, object]
    groups: dict[str, object]
    merchants: dict[str, object]
    indeterminate: dict[str, object]
    directed_penalties: list[object]
    point_penalties: list[object]
    core_score: object
    food_score: object
    concentration_penalty: object
    total_cost: object
    total_surplus: object


def _f(value: Decimal | int | float) -> float:
    return float(value)


def _all_targets(snapshot: PlanningInputSnapshot) -> tuple[TargetDimension, ...]:
    return (
        TargetDimension("ENERCC", TargetKind.POINT, point=snapshot.energy_target_kcal),
        *snapshot.targets,
    )


def _add_penalty(model: Model, target: TargetDimension, amount, name: str):
    penalty = model.addVar(name=name, vtype="C", lb=0.0)
    if target.kind in {TargetKind.ADEQUACY_FLOOR, TargetKind.LOWER_BOUND}:
        if target.lower is None or target.lower <= 0:
            raise ValueError(f"{name}: missing positive lower bound")
        lower = _f(target.lower)
        model.addCons(penalty >= (lower - amount) / lower, name=f"{name}_low")
        return penalty, "directed"
    if target.kind == TargetKind.UPPER_BOUND:
        if target.upper is None or target.upper <= 0:
            raise ValueError(f"{name}: missing positive upper bound")
        upper = _f(target.upper)
        model.addCons(penalty >= (amount - upper) / upper, name=f"{name}_high")
        return penalty, "directed"
    if target.kind == TargetKind.INTERVAL:
        if target.lower is None or target.upper is None or target.lower <= 0 or target.upper <= 0:
            raise ValueError(f"{name}: invalid interval")
        lower, upper = _f(target.lower), _f(target.upper)
        model.addCons(penalty >= (lower - amount) / lower, name=f"{name}_low")
        model.addCons(penalty >= (amount - upper) / upper, name=f"{name}_high")
        return penalty, "directed"
    if target.kind == TargetKind.POINT:
        if target.point is None or target.point <= 0:
            raise ValueError(f"{name}: missing positive point")
        lower = _f(target.point * Decimal("0.95"))
        upper = _f(target.point * Decimal("1.05"))
        model.addCons(penalty >= (lower - amount) / lower, name=f"{name}_low")
        model.addCons(penalty >= (amount - upper) / upper, name=f"{name}_high")
        return penalty, "point"
    raise ValueError(f"unsupported target kind {target.kind}")


def _add_indeterminate_semantics(
    model: Model,
    *,
    target: TargetDimension,
    known_amount,
    unknown_quantities: list[object],
    index: int,
):
    unknown_used = model.addVar(name=f"unknown_{index}_{target.measure}", vtype="B")
    for quantity in unknown_quantities:
        # If unknown_used == 0 no quantitatively unknown food may contribute.
        # Any positive selected quantity therefore forces unknown_used == 1.
        model.addConsIndicator(quantity <= 0, binvar=unknown_used, activeone=False)

    if target.kind not in {TargetKind.ADEQUACY_FLOOR, TargetKind.LOWER_BOUND}:
        return unknown_used

    if target.lower is None or target.lower <= 0:
        raise ValueError(f"{target.measure}: lower-bound target requires a positive lower value")

    # For adequacy/lower-bound semantics, unknown evidence does not make compliance
    # indeterminate when known contributions alone already prove the floor.
    proven_from_known = model.addVar(name=f"proven_{index}_{target.measure}", vtype="B")
    model.addConsIndicator(
        known_amount >= _f(target.lower),
        binvar=proven_from_known,
        activeone=True,
    )
    indeterminate = model.addVar(name=f"indet_{index}_{target.measure}", vtype="B")
    model.addCons(indeterminate >= unknown_used - proven_from_known)
    model.addCons(indeterminate <= unknown_used)
    model.addCons(indeterminate <= 1 - proven_from_known)
    return indeterminate


def _build_model(snapshot: PlanningInputSnapshot) -> tuple[Model, _Vars]:
    model = Model("nutrition-management")
    model.hideOutput()
    model.setIntParam("parallel/maxnthreads", 1)
    model.setIntParam("randomization/randomseedshift", 0)
    model.setIntParam("randomization/permutationseed", 0)
    model.setIntParam("randomization/lpseed", 0)

    candidates = tuple(sorted(snapshot.candidates, key=lambda item: item.offer_id))
    if not candidates:
        raise HardModelInfeasible("no executable offers in planning snapshot")

    packages = {
        item.offer_id: model.addVar(name=f"pkg_{item.offer_id}", vtype="I", lb=0.0)
        for item in candidates
    }
    planned = {
        item.offer_id: model.addVar(name=f"qty_{item.offer_id}", vtype="C", lb=0.0)
        for item in candidates
    }
    for item in candidates:
        model.addCons(
            planned[item.offer_id] <= _f(item.edible_grams_per_package) * packages[item.offer_id],
            name=f"package_capacity_{item.offer_id}",
        )
    model.addCons(quicksum(packages.values()) >= 1, name="non_empty_basket")

    by_channel: dict[str, list] = defaultdict(list)
    by_merchant: dict[str, set[str]] = defaultdict(set)
    by_currency: dict[str, list] = defaultdict(list)
    for item in candidates:
        by_channel[item.channel_id].append(item)
        by_merchant[item.merchant_id].add(item.channel_id)
        by_currency[item.currency].append(item)

    groups = {key: model.addVar(name=f"group_{key}", vtype="B") for key in sorted(by_channel)}
    merchants = {key: model.addVar(name=f"merchant_{key}", vtype="B") for key in sorted(by_merchant)}
    currencies = {key: model.addVar(name=f"currency_{key}", vtype="B") for key in sorted(by_currency)}
    free_delivery: dict[str, object] = {}

    for channel_id, items in sorted(by_channel.items()):
        group = groups[channel_id]
        subtotal = quicksum(_f(item.package_price) * packages[item.offer_id] for item in items)
        for item in items:
            model.addConsIndicator(packages[item.offer_id] <= 0, binvar=group, activeone=False)
        sample = items[0]
        if sample.minimum_order > 0:
            model.addConsIndicator(subtotal >= _f(sample.minimum_order), binvar=group, activeone=True)
        if sample.free_delivery_threshold is not None and sample.fulfilment_fee > 0:
            free = model.addVar(name=f"free_{channel_id}", vtype="B")
            free_delivery[channel_id] = free
            model.addCons(free <= group)
            model.addConsIndicator(
                subtotal >= _f(sample.free_delivery_threshold),
                binvar=free,
                activeone=True,
            )

    for merchant_id, channel_ids in sorted(by_merchant.items()):
        merchant = merchants[merchant_id]
        for channel_id in sorted(channel_ids):
            model.addConsIndicator(groups[channel_id] <= 0, binvar=merchant, activeone=False)

    for currency, items in sorted(by_currency.items()):
        marker = currencies[currency]
        for item in items:
            model.addConsIndicator(packages[item.offer_id] <= 0, binvar=marker, activeone=False)
    model.addCons(quicksum(currencies.values()) <= 1, name="single_currency")

    indeterminate: dict[str, object] = {}
    directed_penalties: list[object] = []
    point_penalties: list[object] = []
    for index, target in enumerate(_all_targets(snapshot)):
        known_terms = []
        unknown_quantities = []
        for item in candidates:
            evidence = item.nutrient(target.measure)
            if evidence.status in {EvidenceStatus.TRACE, EvidenceStatus.MISSING}:
                unknown_quantities.append(planned[item.offer_id])
            elif evidence.amount_per_100g is not None:
                known_terms.append(_f(evidence.amount_per_100g / Decimal(100)) * planned[item.offer_id])
        known_amount = quicksum(known_terms) if known_terms else 0.0
        indeterminate[f"{index}:{target.measure}:{target.kind.value}"] = _add_indeterminate_semantics(
            model,
            target=target,
            known_amount=known_amount,
            unknown_quantities=unknown_quantities,
            index=index,
        )
        penalty, family = _add_penalty(model, target, known_amount, f"pen_{index}_{target.measure}")
        if family == "point":
            point_penalties.append(penalty)
        else:
            directed_penalties.append(penalty)

    # Variety representation is based on planned utilized quantity. Threshold comparisons
    # are linear expressions; concentration itself is a ratio and SCIP handles the small
    # nonlinear constraint directly for this first validation slice.
    food_ids = sorted({item.base_food_id for item in candidates})
    food_rep = {food_id: model.addVar(name=f"foodrep_{food_id}", vtype="B") for food_id in food_ids}
    mass_rep = {food_id: model.addVar(name=f"massrep_{food_id}", vtype="B") for food_id in food_ids}
    energy_rep = {food_id: model.addVar(name=f"energyrep_{food_id}", vtype="B") for food_id in food_ids}

    total_mass = quicksum(planned[item.offer_id] for item in candidates)
    energy_terms = []
    food_mass = {}
    food_energy = {}
    for food_id in food_ids:
        food_items = [item for item in candidates if item.base_food_id == food_id]
        food_mass[food_id] = quicksum(planned[item.offer_id] for item in food_items)
        terms = []
        for item in food_items:
            evidence = item.nutrient("ENERCC")
            if evidence.amount_per_100g is not None:
                term = _f(evidence.amount_per_100g / Decimal(100)) * planned[item.offer_id]
                terms.append(term)
                energy_terms.append(term)
        food_energy[food_id] = quicksum(terms) if terms else 0.0
        model.addConsIndicator(
            food_mass[food_id] >= 0.01 * total_mass,
            binvar=mass_rep[food_id],
            activeone=True,
        )
        model.addCons(food_rep[food_id] >= mass_rep[food_id])
        model.addCons(food_rep[food_id] >= energy_rep[food_id])
        model.addCons(food_rep[food_id] <= mass_rep[food_id] + energy_rep[food_id])

    total_energy = quicksum(energy_terms) if energy_terms else 0.0
    for food_id in food_ids:
        model.addConsIndicator(
            food_energy[food_id] >= 0.01 * total_energy,
            binvar=energy_rep[food_id],
            activeone=True,
        )

    categories = sorted({item.category for item in candidates if item.category in _CORE_CATEGORIES})
    category_rep = {category: model.addVar(name=f"catrep_{category}", vtype="B") for category in categories}
    for category in categories:
        represented = [
            food_rep[food_id]
            for food_id in food_ids
            if any(item.base_food_id == food_id and item.category == category for item in candidates)
        ]
        model.addCons(category_rep[category] <= quicksum(represented))

    core_score = model.addVar(name="core_score", vtype="C", lb=0.0, ub=4.0)
    if category_rep:
        model.addCons(core_score <= quicksum(category_rep.values()))
    else:
        model.addCons(core_score <= 0)
    food_score = model.addVar(name="food_score", vtype="C", lb=0.0, ub=8.0)
    model.addCons(food_score <= quicksum(food_rep.values()))

    max_share = model.addVar(name="max_food_energy_share", vtype="C", lb=0.0, ub=1.0)
    if energy_terms:
        for food_id in food_ids:
            model.addCons(food_energy[food_id] <= max_share * total_energy)
    concentration_penalty = model.addVar(name="concentration_penalty", vtype="C", lb=0.0)
    model.addCons(concentration_penalty >= max_share - 0.25)

    package_cost = quicksum(_f(item.package_price) * packages[item.offer_id] for item in candidates)
    fee_terms = []
    for channel_id, items in sorted(by_channel.items()):
        fee = _f(items[0].fulfilment_fee)
        if fee == 0:
            continue
        if channel_id in free_delivery:
            fee_terms.append(fee * (groups[channel_id] - free_delivery[channel_id]))
        else:
            fee_terms.append(fee * groups[channel_id])
    total_cost = package_cost + quicksum(fee_terms)
    total_surplus = quicksum(
        _f(item.edible_grams_per_package) * packages[item.offer_id] - planned[item.offer_id]
        for item in candidates
    )

    return model, _Vars(
        packages=packages,
        planned=planned,
        groups=groups,
        merchants=merchants,
        indeterminate=indeterminate,
        directed_penalties=directed_penalties,
        point_penalties=point_penalties,
        core_score=core_score,
        food_score=food_score,
        concentration_penalty=concentration_penalty,
        total_cost=total_cost,
        total_surplus=total_surplus,
    )


def _optimize_stage(
    model: Model,
    expression,
    *,
    sense: str,
    name: str,
    allow_initial_infeasible: bool = False,
    fix: bool = True,
) -> float:
    model.setObjective(expression, sense)
    model.optimize()
    status = str(model.getStatus()).lower()
    if status == "infeasible" and allow_initial_infeasible:
        raise HardModelInfeasible("hard executability model is infeasible")
    if status != "optimal":
        raise SolverTechnicalFailure(f"solver stage {name!r} ended with {status!r}, not proven optimal")
    optimum = float(model.getObjVal())
    model.freeTransform()
    if fix:
        if sense == "minimize":
            model.addCons(expression <= optimum + _EPS, name=f"fix_{name}")
        else:
            model.addCons(expression >= optimum - _EPS, name=f"fix_{name}")
    return optimum


def solve(snapshot: PlanningInputSnapshot) -> SolverDecision:
    model, vars_ = _build_model(snapshot)

    _optimize_stage(
        model,
        quicksum(vars_.indeterminate.values()),
        sense="minimize",
        name="indeterminate",
        allow_initial_infeasible=True,
    )

    directed_max = model.addVar(name="directed_max", vtype="C", lb=0.0)
    for penalty in vars_.directed_penalties:
        model.addCons(directed_max >= penalty)
    _optimize_stage(model, directed_max, sense="minimize", name="directed_max")
    _optimize_stage(model, quicksum(vars_.directed_penalties), sense="minimize", name="directed_mean")

    point_max = model.addVar(name="point_max", vtype="C", lb=0.0)
    for penalty in vars_.point_penalties:
        model.addCons(point_max >= penalty)
    _optimize_stage(model, point_max, sense="minimize", name="point_max")
    _optimize_stage(model, quicksum(vars_.point_penalties), sense="minimize", name="point_mean")

    _optimize_stage(model, vars_.core_score, sense="maximize", name="variety_categories")
    _optimize_stage(model, vars_.food_score, sense="maximize", name="variety_foods")
    _optimize_stage(model, vars_.concentration_penalty, sense="minimize", name="variety_concentration")

    minimum_cost = _optimize_stage(
        model,
        vars_.total_cost,
        sense="minimize",
        name="minimum_cost",
        fix=False,
    )
    model.addCons(vars_.total_cost <= minimum_cost * 1.05 + _EPS, name="cost_close")

    _optimize_stage(model, quicksum(vars_.groups.values()), sense="minimize", name="purchase_groups")
    _optimize_stage(model, quicksum(vars_.merchants.values()), sense="minimize", name="merchants")
    _optimize_stage(model, vars_.total_cost, sense="minimize", name="close_cost")
    _optimize_stage(model, vars_.total_surplus, sense="minimize", name="surplus")

    # Stable non-business technical total order among otherwise business-equivalent optima.
    for offer_id in sorted(vars_.packages):
        _optimize_stage(model, vars_.packages[offer_id], sense="minimize", name=f"tech_pkg_{offer_id}")
        _optimize_stage(model, vars_.planned[offer_id], sense="minimize", name=f"tech_qty_{offer_id}")

    model.optimize()
    if str(model.getStatus()).lower() != "optimal":
        raise SolverTechnicalFailure("final fixed model did not remain optimal")

    lines = []
    for offer_id in sorted(vars_.packages):
        package_count = int(round(model.getVal(vars_.packages[offer_id])))
        planned_grams = Decimal(str(model.getVal(vars_.planned[offer_id])))
        if package_count or planned_grams > 0:
            lines.append(SolverLineDecision(offer_id, package_count, planned_grams))
    return SolverDecision(lines=tuple(lines))
