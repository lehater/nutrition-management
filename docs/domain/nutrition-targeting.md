# Nutrition Targeting

Status: `accepted` for the current MVP tactical baseline.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.

## Purpose

Own the semantic facts required to derive the 30-day nutritional target that Purchase Planning consumes.

## Authoritative state

### Household

A household is the calculation scope containing one or more Household Members.

### Household Member

A Household Member is a person whose current Nutrition Profile contributes to household nutritional demand.

The MVP keeps one current profile per member; profile history and multiple saved scenarios are not required.

### Nutrition Profile

Current source inputs:
- age;
- sex;
- height;
- current weight;
- current-weight date;
- target weight;
- target date;
- physical activity level;
- development/growth stage.

The profile describes source facts and goals. It does not contain authoritative nutrient targets.

### Nutrition Standard Set

Versioned reference data used to derive energy, macro- and micronutrient target ranges.

Required provenance:
- source name;
- version;
- effective date when available;
- active/inactive state.

The MVP uses exactly one active Nutrition Standard Set by default. The controlled nutrient set is defined by the active standard set rather than hard-coded independently in the optimizer.

## Derived state

### Member Nutrition Target

A rebuildable 30-day set of target ranges derived from a member's Nutrition Profile and the active Nutrition Standard Set.

It includes energy, macro- and micronutrient ranges defined by the applicable standards. Weight-change intent is derived from current weight/current-weight date and target weight/target date.

The derivation must retain provenance sufficient to identify the profile inputs and standard-set version used.

### Household Nutrition Target

A rebuildable 30-day aggregation of Member Nutrition Targets used by the MVP Purchase Planning context.

Individual member targets remain available as derivation evidence, but the MVP optimizer consumes the aggregated household target.

## Domain operations

- derive a Member Nutrition Target from one current profile and the active standard set;
- aggregate member targets into the Household Nutrition Target;
- detect that a previously derived target is stale when source profile inputs or the active standard set change.

## Invariants

- the MVP calculation period is 30 days;
- nutrient goals are target ranges, not single threshold values;
- derived targets never become the source of truth for member parameters or standards;
- every derived target identifies the standards provenance used;
- a household target is calculated only from current member targets for the same calculation period.

## Explicit exclusions

The current model does not own medical restrictions, allergies, intolerances, therapeutic diets, actual food consumption or food allocation to individual members.

## Material unknowns before architecture

- the concrete active standards source/version;
- exact energy-expenditure and weight-change formulas;
- exact vocabulary/rules for physical-activity levels and growth/development stages.
