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

For derivation, physical activity is resolved to the numeric PAL semantics defined by the active Nutrition Standard Set. Development/growth-stage vocabulary remains a separate unresolved semantic concern; age already determines the ordinary infant/child/adolescent/adult applicability used by `mvp-v1`.

### Nutrition Standard Set

A Nutrition Standard Set is a versioned, sourced composition of:

- nutrient references and their applicability;
- source semantic kinds such as recommended intake, estimated value and guideline;
- safety limits where available;
- energy/PAL derivation policy;
- weight-goal energy policy.

The MVP uses exactly one active version by default. The current active version is [`mvp-v1`](nutrition-standard-set-mvp-v1.md), accepted by [`ADR-003`](../decisions/ADR-003-nutrition-targeting-standards-and-derivation.md).

A standard-set version is immutable once used as derivation provenance. A changed upstream source, erratum or product formula produces a new standard-set version rather than silently changing the meaning of an existing derived target.

The controlled nutrient set is defined by the active standard set together with nutrient identities that Food Knowledge can represent; it is not hard-coded independently in Purchase Planning.

### Nutrient Reference

A sourced reference used to express desired/adequate intake for an applicable population or member basis.

A Nutrient Reference preserves:

- nutrient identity;
- applicability conditions;
- source semantic kind;
- native basis, such as amount/day, amount/kg/day, percentage of energy or amount/1000 kcal;
- source value, bound or interval;
- source/version provenance.

A point reference remains a point. Nutrition Targeting does not manufacture an arbitrary preferred interval merely because downstream optimization works more conveniently with ranges.

### Safety Limit

A sourced upper-safety semantic, such as an EFSA Tolerable Upper Intake Level (UL) or safe level, when applicable to the exact nutrient form represented by the product.

A Safety Limit is not the upper edge of a preferred target range. It is retained separately from Nutrient Reference semantics.

## Derived state

### Member Nutrition Target

A rebuildable 30-day target specification derived from one member's Nutrition Profile and the active Nutrition Standard Set.

It contains, as applicable:

- final energy target;
- resolved macro- and micronutrient references, preserving whether each result is a point, lower/upper bound or interval;
- separate safety limits where semantically applicable;
- derivation provenance sufficient to identify profile inputs, resolved PAL, formula/policy choices and standard-set version.

The complete `mvp-v1` formulas and source policy are owned by [`nutrition-standard-set-mvp-v1.md`](nutrition-standard-set-mvp-v1.md).

#### Energy derivation summary

- age `< 1`: use DGE age/sex infant energy guiding values;
- age `1–<19`: `maintenance energy = Henry REE × PAL × 1.01`;
- age `>= 19`: calculate DGE adult REE from age/current weight/sex, then `maintenance energy = REE × PAL`;
- age `>= 19` with an active target-weight/date goal: use the accepted NIDDK/Hall dynamic body-weight model to derive the final energy target;
- age `< 19`: target weight/date do not automatically change energy in the MVP.

Percent-of-energy nutrient references are resolved against the final energy target after any applicable adult weight-goal adjustment.

#### Thirty-day derivation

Daily source references are resolved on their native basis and then scaled to the fixed 30-day Calculation Period. Source intervals preserve both bounds; source point values remain points.

### Household Nutrition Target

A rebuildable 30-day aggregation of Member Nutrition Targets used by the MVP Purchase Planning context.

Compatible adequacy/reference quantities aggregate additively by nutrient. Individual member targets remain available as derivation evidence.

Member safety limits do not become a household-level guarantee of individual safety. Under ADR-002 the MVP optimizer does not prove allocation of purchased food among members, so summing individual ULs cannot prove that each member will remain below their own limit.

## Domain operations

- resolve the active Nutrition Standard Set;
- resolve a member's numeric PAL from the accepted activity semantics;
- derive maintenance energy from age/sex/height/current weight/PAL under the active set;
- apply the accepted adult weight-goal policy when applicable;
- resolve source-native nutrient references against member/profile/energy bases;
- attach applicable safety limits without conflating them with preferred targets;
- derive a 30-day Member Nutrition Target;
- aggregate compatible member adequacy/reference demand into the Household Nutrition Target;
- detect that a previously derived target is stale when source profile inputs or the active standard-set version change.

## Invariants

- the MVP Calculation Period is 30 days;
- exactly one Nutrition Standard Set is active by default in the MVP;
- a derived target identifies the immutable standard-set version used;
- source reference kind is preserved through derivation;
- a safety limit is never reinterpreted as a preferred target maximum;
- source point references are not silently expanded into arbitrary ranges;
- relative references are resolved using the basis required by their source, not a universal current-weight assumption;
- adult weight-goal adjustment uses the accepted dynamic model and is not silently replaced by a fixed kcal-per-kilogram rule;
- pediatric target weight/date do not alter energy without a separately accepted pediatric policy;
- derived targets never become the source of truth for member parameters or standards;
- a household target is calculated only from current member targets for the same Calculation Period and standard-set version.

## Explicit exclusions

The current model does not own medical restrictions, allergies, intolerances, therapeutic diets, actual food consumption or food allocation to individual members.

Pregnancy/lactation reference rows may exist in the sourced standard set, but they are not selected until an explicit physiological-state concept and applicability rules are accepted.

## Material unknowns before architecture

- exact vocabulary and lifecycle semantics for development/growth/physiological state, including whether pregnancy/lactation belongs in the MVP profile at all;
- canonical nutrient identities, measurement units/conversions and rounding policy required to match Nutrition Targeting references to Food Knowledge quantities.
