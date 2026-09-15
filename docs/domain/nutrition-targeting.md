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
- date of birth;
- sex;
- height;
- current weight;
- current-weight date;
- target weight;
- target date;
- physical activity level.

The profile describes source facts and goals. It does not contain authoritative nutrient targets.

`Date of birth`, rather than a mutable entered age, is the authoritative age source. Chronological age and the applicable source age band are derived at target-derivation time. This is required because the active reference data includes sub-year infant age bands and because age changes without a profile edit.

For `mvp-v1`, sex is the male/female applicability input required by sex-specific DGE/ÖGE rows and energy formulas. This field exists for nutrition-standard applicability; it is not a model of gender identity.

`Current weight` is an observed planning baseline whose observation date must not be later than the target-derivation date. `mvp-v1` does not extrapolate a different current weight from the age of that observation; the observation date remains provenance.

For members aged one year or older, physical activity is a resolved numeric PAL input governed by the active Nutrition Standard Set. `mvp-v1` supports an unadjusted PAL of `1.2–2.4`; the documented strenuous-activity adjustment may raise the final PAL by `0.3`, to at most `2.7`. It never silently chooses a midpoint from a descriptive PAL range. PAL is not required for members under one year because infant energy uses source guiding values independently of PAL.

The MVP has no independent `development/growth stage` profile input. Ordinary infant/child/adolescent/adult applicability and the pediatric growth-energy factor are derived from date of birth and the active standard set, avoiding a second source of truth that could contradict chronological age.

Pregnancy and lactation are not modeled as member physiological states in the MVP. Corresponding source rows may exist in the standard source but are outside active MVP applicability.

The MVP also does not add phytate-intake class, menstruation state or menopause state solely to force selection of every DGE source variant. When a source family needs one of those facts, applicability remains explicit and unresolved under ADR-012 rather than being defaulted or inferred.

### Nutrition Standard Set

A Nutrition Standard Set is a versioned, sourced composition of:

- nutrient reference families, source variants and their applicability;
- source semantic kinds such as recommended intake, estimated value and guideline;
- safety limits where available;
- energy/PAL derivation policy;
- source-owned relative/reference-weight rules;
- weight-goal energy policy.

The MVP uses exactly one active version by default. The current active version is [`mvp-v1`](nutrition-standard-set-mvp-v1.md), accepted by [`ADR-003`](../decisions/ADR-003-nutrition-targeting-standards-and-derivation.md) and refined by [`ADR-012`](../decisions/ADR-012-source-applicability-and-protein-weight-basis.md).

A standard-set version is immutable once used as derivation provenance. A changed upstream source, erratum or product formula produces a new standard-set version rather than silently changing the meaning of an existing derived target.

Canonical nutrient identity, unit, food-basis and target-to-food mapping semantics are defined in [`nutrient-semantics.md`](nutrient-semantics.md) and accepted by [`ADR-004`](../decisions/ADR-004-canonical-nutrient-semantics.md).

The optimizer-controlled nutrient set is the intersection of quantitatively resolved active standard references and Food Knowledge canonical components/derived Nutrient Measures with accepted semantic mappings. It is not hard-coded independently in Purchase Planning.

### Nutrient Reference

A sourced reference used to express desired/adequate intake for an applicable population or member basis.

A stable reference family may contain multiple source variant rows. Each row preserves:

- stable family identity and source-row identity;
- nutrient identity;
- applicability conditions;
- source semantic kind;
- native basis, such as amount/day, amount/kg/day, percentage of energy or amount/1000 kcal;
- source unit;
- source value, bound or interval;
- source/version/citation provenance.

A family resolves to a quantitative target only when accepted profile facts and deterministic standard-set policy select exactly one active variant. If a potentially applicable family needs a source factor that the MVP does not own, the member target records `unsupported_applicability`. If known member facts place the member outside the general source reference, it records `source_inapplicable`. Rows intentionally outside product scope, such as pregnancy/lactation rows, remain source provenance rather than active target gaps.

A point reference remains a point. Nutrition Targeting does not manufacture an arbitrary preferred interval merely because downstream optimization works more conveniently with ranges.

### Safety Limit

A sourced upper-safety semantic, such as an EFSA Tolerable Upper Intake Level (UL) or safe level, when applicable to the exact nutrient form represented by the product.

A Safety Limit is not the upper edge of a preferred target range. It is retained separately from Nutrient Reference semantics.

A Safety Limit becomes quantitatively enforceable only when its substance/form scope has an accepted mapping to Food Knowledge data at compatible semantic specificity. Otherwise it remains diagnostic/provenance information rather than a false hard constraint.

## Derived state

### Member Nutrition Target

A rebuildable 30-day target specification derived from one member's Nutrition Profile and the active Nutrition Standard Set.

It contains, as applicable:

- derivation date;
- chronological age and selected source age band at derivation time;
- final energy target;
- resolved macro- and micronutrient references, preserving family/row identity and whether each result is a point, lower/upper bound or interval;
- unresolved active reference-family applicability gaps, including resolution state, missing dimensions and candidate source-row identities;
- separate safety limits where semantically applicable;
- derivation provenance sufficient to identify profile inputs, resolved PAL, applicable-weight rules, formula/policy choices and standard-set version.

The complete `mvp-v1` formulas and source policy are owned by [`nutrition-standard-set-mvp-v1.md`](nutrition-standard-set-mvp-v1.md).

#### Energy derivation summary

- age `< 1`: use DGE age/sex infant energy guiding values;
- age `1–<19`: `maintenance energy = Henry REE × PAL × 1.01`;
- age `>= 19`: calculate DGE adult REE from age/current weight/sex, then `maintenance energy = REE × PAL`;
- age `>= 19` with an active target-weight/date goal: use the accepted NIDDK/Hall dynamic body-weight model to derive the final energy target;
- age `< 19`: target weight/date do not automatically change energy in the MVP.

Percent-of-energy nutrient references are resolved against the final energy target after any applicable adult weight-goal adjustment.

#### Source applicability summary

- a reference family becomes numeric only when exactly one active source variant can be selected from accepted MVP facts/policy;
- missing phytate class makes adult zinc `unsupported_applicability`;
- missing menstruation/menopause state makes affected female iron families `unsupported_applicability`;
- adult DGE protein uses current weight for normal BMI and BMI-22 reference weight for overweight BMI, while BMI `<18.5` or `>=30.0` makes the general DGE protein reference `source_inapplicable`;
- no source applicability default is invented merely to maximize quantitative coverage.

#### Thirty-day derivation

The MVP selects chronological age and the applicable age band at the derivation date, then uses that applicability for the whole 30-day Calculation Period. Crossing an age-band boundary during that period does not split one target into multiple subperiods in the MVP.

Daily source references are resolved on their native basis and then scaled to the fixed 30-day Calculation Period. Source intervals preserve both bounds; source point values remain points. An unresolved applicability gap has no fabricated 30-day numeric quantity.

### Household Nutrition Target

A rebuildable 30-day aggregation of Member Nutrition Targets used by the MVP Purchase Planning context.

Compatible resolved adequacy/reference quantities aggregate additively by nutrient. Individual member targets remain available as derivation evidence.

Member-level `unsupported_applicability` and `source_inapplicable` gaps are preserved in Household Nutrition Target as unsupported coverage. They are not converted to zero demand and do not disappear during aggregation.

Member safety limits do not become a household-level guarantee of individual safety. Under ADR-002 the MVP optimizer does not prove allocation of purchased food among members, so summing individual ULs cannot prove that each member will remain below their own limit.

## Domain operations

- resolve the active Nutrition Standard Set;
- derive chronological age and applicable source age band from date of birth at the derivation date;
- validate current-weight observation applicability without inventing a new current weight;
- validate/use the resolved numeric PAL under the active standard-set rules when PAL is required;
- derive maintenance energy from age/sex/height/current weight/PAL under the active set;
- apply the accepted adult weight-goal policy when applicable;
- evaluate source-family applicability without inventing missing source factors;
- resolve source-native nutrient references against member/profile/energy/reference-weight bases;
- map resolved target references to canonical Food Knowledge components/derived Nutrient Measures using the accepted crosswalk;
- preserve unresolved active applicability as explicit unsupported coverage;
- attach applicable safety limits without conflating them with preferred targets;
- derive a 30-day Member Nutrition Target;
- aggregate compatible resolved member adequacy/reference demand and preserve member applicability gaps in the Household Nutrition Target;
- detect that a previously derived target is stale when source profile inputs or the active standard-set version change.

## Invariants

- the MVP Calculation Period is 30 days;
- exactly one Nutrition Standard Set is active by default in the MVP;
- date of birth is the authoritative member age source; entered age is not independent authoritative state;
- age and age band are derived at target-derivation time and retained as provenance;
- current-weight date is not later than derivation date, and observed current weight is not silently extrapolated;
- PAL is not required for age `< 1` under `mvp-v1`;
- for age `>= 1`, a resolved numeric PAL is required and must satisfy the active standard-set rules; invalid PAL values are not clamped or defaulted;
- the MVP has no independent development/growth-stage state;
- pregnancy/lactation-specific applicability is outside the MVP;
- phytate, menstruation and menopause are not inferred/defaulted from other profile facts;
- a derived target identifies the immutable standard-set version used;
- source reference family, selected row identity and source semantic kind are preserved through derivation;
- a reference family requires exactly one applicable active variant before it becomes a numeric target;
- unresolved required applicability is explicit unsupported coverage rather than zero or omission;
- target-to-food comparability requires an accepted semantic nutrient mapping;
- a safety limit is never reinterpreted as a preferred target maximum;
- source point references are not silently expanded into arbitrary ranges;
- relative references are resolved using the basis required by their source, not a universal current-weight assumption;
- adult protein applicable weight follows ADR-012 and never overwrites current-weight state;
- adult weight-goal adjustment uses the accepted dynamic model and is not silently replaced by a fixed kcal-per-kilogram rule;
- pediatric target weight/date do not alter energy without a separately accepted pediatric policy;
- derived targets never become the source of truth for member parameters or standards;
- a household target is calculated only from current member targets for the same Calculation Period and standard-set version.

## Explicit exclusions

The current model does not own pregnancy/lactation-specific targeting, phytate-intake profiling, menstruation/menopause profiling, medical restrictions, allergies, intolerances, therapeutic diets, actual food consumption or food allocation to individual members.

## Material unknowns before architecture

None for the accepted MVP scope after ADR-012; source dimensions that the MVP intentionally does not own are represented explicitly as unsupported applicability rather than unresolved domain semantics.
