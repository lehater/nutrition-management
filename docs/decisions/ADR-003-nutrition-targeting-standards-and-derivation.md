# ADR-003 — Nutrition Targeting uses a composite sourced standard set

Status: `accepted`.

Date: 2026-09-15.

## Context

S1 requires versioned, sourced nutrition standards and individual derivation of energy, macro- and micronutrient targets. Before S3 Architecture, Nutrition Targeting must therefore fix both the active MVP source set and the semantic rules by which a member profile becomes a target.

The relevant source material does not expose one homogeneous `[minimum, maximum]` interval per nutrient. DGE/ÖGE publishes different kinds of reference values, including recommended intakes, estimated values and guideline values. EFSA Tolerable Upper Intake Levels (ULs) express safety ceilings for chronic intake rather than preferred target maxima. Energy also requires a derivation policy from anthropometric data and physical activity rather than a static nutrient-table lookup.

The member profile additionally contains a target weight and target date. A fixed energy-per-kilogram weight-change rule would ignore the dynamic adaptation of energy expenditure over time and would be unsuitable as the canonical product rule.

DGE/ÖGE applicability is age-sensitive, including sub-year infant bands, and age changes without an explicit profile edit. Keeping both entered age and a separate development/growth stage would therefore create two mutable facts for one underlying applicability dimension and permit contradictions.

## Decision

### Active Nutrition Standard Set

The MVP active set is `mvp-v1` and is defined in [`../domain/nutrition-standard-set-mvp-v1.md`](../domain/nutrition-standard-set-mvp-v1.md).

It composes four sourced policies:

1. **DGE/ÖGE reference values** — `Referenzwerte für die Nährstoffzufuhr`, 3rd edition, 1st issue (2025), including the published erratum dated May 2026. This is the primary source for nutrient-reference semantics and values.
2. **DGE energy derivation** — the DGE energy reference derivation and current DGE energy FAQ, including resting-energy equations and PAL semantics. For children and adolescents the DGE derivation uses Henry (2005) equations and the growth factor described by DGE.
3. **EFSA upper-intake limits** — `Overview on Tolerable Upper Intake Levels`, version 11 (August 2025). These values are safety limits only.
4. **NIDDK/Hall adult body-weight model** — the dynamic model underlying the NIDDK Body Weight Planner, used only for adult weight-goal energy adjustment.

A standard-set version freezes the concrete source versions and product derivation policy. A later upstream publication does not silently mutate `mvp-v1`; adopting changed values or rules requires a new Nutrition Standard Set version and explicit activation.

### Member applicability semantics

The MVP Nutrition Profile stores `date of birth`, not an independently authoritative entered age. Chronological age and the applicable source age band are derived at the target-derivation date. Exact calendar boundaries are used for age-band selection, including sub-year infant bands.

For KISS, the age/age-band selected at derivation time applies to the whole fixed 30-day Calculation Period; the MVP does not split one target when a birthday or source age-band boundary occurs inside that period.

The MVP has no independent `development/growth stage` input. Ordinary infant/child/adolescent/adult applicability and the pediatric growth-energy factor are consequences of chronological age plus `mvp-v1` policy.

Sex remains a profile input because DGE/ÖGE reference rows and energy equations may distinguish male and female applicability. In this context it is a nutrition-standard applicability fact, not a model of gender identity.

Pregnancy and lactation are separate special physiological situations in the source standards. They are outside the MVP requirements and are therefore not modeled as member state or selected by `mvp-v1`. Supporting them later requires an explicit physiological-state extension rather than overloading age or growth-stage semantics.

### Nutrient-reference semantics

A resolved nutrient target preserves the semantic kind of the source reference. In particular:

- a recommended intake or estimated value remains a reference value;
- a guideline may remain a point, lower bound, upper bound or interval according to the source;
- a relative reference such as amount per kg body weight, percentage of energy or amount per 1000 kcal is resolved using the basis defined by the active set;
- an EFSA UL or safe level remains a separate safety limit.

The system must not reinterpret an EFSA UL as the upper edge of a preferred nutritional range, and it must not invent a preferred interval around a source value that is published as a point reference.

### Energy derivation

For members under 1 year, the active set uses the DGE age/sex energy guiding values rather than a PAL-based individual equation.

For members from 1 year to under 19 years, resting energy expenditure is calculated with the Henry (2005) sex/age equation selected by the active set, and growth is included as:

`maintenance energy = REE × PAL × 1.01`.

For members aged 19 years or older, resting energy expenditure is calculated with the DGE equations:

- female: `REE kcal/day = (0.047 × weight_kg - 0.01452 × age_years + 3.21) × 239`;
- male: `REE kcal/day = (0.047 × weight_kg + 1.009 - 0.01452 × age_years + 3.21) × 239`.

Adult maintenance energy is then:

`maintenance energy = REE × PAL`.

PAL is a numeric domain input resolved according to the DGE activity ranges recorded in `mvp-v1`.

### Weight-goal energy adjustment

If an adult member aged 19 years or older has a target weight different from current weight and a future target date, Nutrition Targeting uses the NIDDK/Hall dynamic body-weight model to derive the energy intake consistent with that goal. The model version and source are part of `mvp-v1` provenance.

The MVP does not replace this model with a static kcal-per-kilogram rule.

For members under 19, target weight/date do not automatically alter the energy target in the MVP. Pediatric weight-goal semantics require a separate accepted policy before such an adjustment can be made.

### Thirty-day derivation

Nutrition Targeting first derives the applicable daily energy/nutrient target specification, then derives the 30-day Member Nutrition Target for the fixed MVP Calculation Period.

For relative nutrient references, conversion is performed from the resolved member basis before period aggregation. Percent-of-energy references use the final energy target, not the pre-weight-goal maintenance estimate.

Member safety limits remain separate from adequacy/reference targets. Consistent with ADR-002, household aggregation cannot turn member-level ULs into a guarantee that every member's intake will remain below their individual safety limit because the MVP does not prove per-member food allocation.

## Consequences

- `Nutrition Standard Set` becomes a composite, versioned domain fact rather than a single undifferentiated table of ranges.
- Member Nutrition Targets preserve reference kind and safety-limit provenance.
- S1 terminology allows point references, relative formulas and separate safety limits instead of requiring every nutrient to have one `[min,max]` target range.
- Date of birth is the stable age source; chronological age/age band become rebuildable derivation facts.
- A separate development/growth-stage field is removed from the MVP profile, eliminating contradictory age/stage state.
- Pregnancy/lactation-specific targeting is explicitly outside the MVP rather than remaining an unresolved applicability state.
- Physical activity is normalized to numeric PAL semantics sourced from DGE.
- Pediatric weight-goal adjustment remains explicitly unsupported rather than being silently calculated with an adult formula.
- Canonical nutrient identity, unit, food-basis and rounding semantics are resolved separately by ADR-004; Nutrition Targeting relies on that accepted crosswalk when a target must be compared with Food Knowledge.
- A future change of source edition, erratum, formula or weight model creates a new Nutrition Standard Set version rather than rewriting `mvp-v1`.

## Alternatives considered

### Keep entered age plus development/growth stage

Rejected because both fields would describe overlapping age/development applicability and could contradict each other. Date of birth is stable evidence from which age and source age bands can be rebuilt.

### Model pregnancy/lactation now

Rejected for MVP because no accepted requirement needs these special physiological states. Adding lifecycle/state semantics solely because the external source contains rows for them would broaden product scope without demonstrated value.

### Use DGE/ÖGE values only

Rejected because desired/reference intake semantics and chronic upper safety limits answer different questions. EFSA provides a maintained European UL source that can be retained separately without distorting DGE/ÖGE reference values.

### Use EFSA values as the sole standard source

Rejected for the MVP because the DGE/ÖGE set provides a coherent primary reference baseline together with the energy/PAL derivation used by this product. EFSA remains the authority for the safety-limit component.

### Treat the DGE/ÖGE reference as the lower bound and EFSA UL as the upper bound of one target range

Rejected because a UL is a safety ceiling, not the upper end of a preferred intake interval.

### Use a fixed energy-per-kilogram rule for target-weight changes

Rejected because body-weight response to an energy imbalance is dynamic. The accepted adult model explicitly represents that behavior and the requested target horizon.

## Supersession

Supersedes: none.
Superseded by: none.
