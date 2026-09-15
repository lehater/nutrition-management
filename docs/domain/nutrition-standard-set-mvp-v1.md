# Nutrition Standard Set — `mvp-v1`

Status: `active` for the MVP.
Lifecycle layer: `S2 Domain Semantics / Tactical DDD`.
Owner: `Nutrition Targeting`.

## Purpose

Freeze the sourced nutrition-reference and derivation policy used to rebuild Member Nutrition Targets. This artifact defines semantic inputs and formulas; it is not a persistence schema or implementation configuration format.

A change to any source edition, corrected value, applicability rule or derivation formula requires a new standard-set version. Existing derived targets retain the standard-set version used to produce them.

## Sources

### Primary nutrient references — DGE/ÖGE

- Source: Deutsche Gesellschaft für Ernährung (DGE) / Österreichische Gesellschaft für Ernährung (ÖGE), `Referenzwerte für die Nährstoffzufuhr`.
- Edition: 3rd edition, 1st issue, 2025.
- Corrections: published erratum, status May 2026.
- Reference page: <https://www.dge.de/wissenschaft/referenzwerte/>

This source owns the MVP adequacy/reference side: age/sex applicability, recommended intakes, estimated values, guideline values and source-native relative bases.

### Energy/PAL derivation — DGE

- Current FAQ: <https://www.dge.de/gesunde-ernaehrung/faq/energiezufuhr/>
- Derivation publication: German Nutrition Society, `New Reference Values for Energy Intake`, Ann Nutr Metab. 2015;66:219–223, DOI `10.1159/000430959`.
- Child/adolescent REE equations: Henry CJ, `Basal metabolic rate studies in humans: measurement and development of new equations`, Public Health Nutr. 2005;8:1133–1152, as used by the DGE derivation.

### Safety limits — EFSA

- Source: European Food Safety Authority, `Overview on Tolerable Upper Intake Levels as derived by the Scientific Committee on Food (SCF) and the EFSA Panel on Dietetic Products, Nutrition and Allergies (NDA)`.
- Version: 11, August 2025.
- Published document: <https://www.efsa.europa.eu/sites/default/files/2024-05/ul-summary-report.pdf>

EFSA ULs and safe levels are safety semantics. They are not preferred target maxima.

### Adult weight-goal adjustment — NIDDK/Hall

- Source: NIDDK, `Research Behind the Body Weight Planner`: <https://www.niddk.nih.gov/research-funding/at-niddk/labs-branches/laboratory-biological-modeling/integrative-physiology-section/research/body-weight-planner>
- Underlying model: Hall KD et al., `Quantification of the effect of energy imbalance on bodyweight`, Lancet. 2011;378(9793):826–837, plus the dynamic-model equations referenced by NIDDK.

The model is used only for weight-goal energy adjustment for members aged 19 years or older. The product restriction is intentionally stricter than the NIDDK tool's adult boundary so that the DGE adolescent energy policy remains coherent through the under-19 age band.

## Source semantic types

A nutrient reference retains its source meaning. The active set recognizes at least:

- `recommended intake` — recommended intake intended to cover the relevant healthy population group;
- `estimated value` — estimated adequate intake when a recommendation cannot be derived with comparable certainty;
- `guideline` — orientation value that may be a point, lower bound, upper bound or interval;
- `safety limit / UL` — maximum chronic total daily intake not expected to pose an adverse-health risk for the applicable population;
- `safe level` — source-specific safety value that remains distinct from a UL where EFSA uses that distinction.

A point reference remains a point reference. A safety limit is not combined with a recommended value to manufacture one preferred interval.

## Applicability dimensions

For active MVP derivation, source applicability may depend on:

- chronological age or age band derived from date of birth at the derivation date;
- sex where the source distinguishes male/female values;
- body weight or a source-defined reference-weight rule;
- final energy target;
- physical activity expressed as PAL.

DGE/ÖGE also contains special reference rows for pregnancy and lactation. `mvp-v1` retains their source provenance but does not select them because pregnancy/lactation-specific targeting is outside the MVP profile and requirements.

There is no independent development/growth-stage input in `mvp-v1`. Ordinary age-group applicability and the pediatric growth-energy factor are selected from chronological age.

### Age-resolution rule

`date_of_birth` is the authoritative profile fact. `derivation_date` is the date on which the 30-day target is derived.

Chronological age and source age band are resolved from those two dates without an independently entered age value. Exact calendar boundaries determine age-band membership, including sub-year infant bands.

For KISS in the MVP, the age/age-band selection at `derivation_date` applies to the whole 30-day Calculation Period. If a member crosses an age-band boundary inside that period, the target is not split into subperiods; a later target derivation will select the newly applicable band.

## Physical Activity Level

The active set represents physical activity as a **resolved numeric PAL multiplier**, not as a second categorical state.

DGE source ranges:

| PAL | Semantic description |
|---|---|
| `1.2–1.3` | exclusively/mostly sitting or lying; frail, immobile or bedridden lifestyle |
| `1.4–1.5` | predominantly sedentary activity with little or no strenuous leisure activity |
| `1.6–1.7` | predominantly sedentary activity with some walking/standing activity |
| `1.8–1.9` | predominantly walking/standing activity |
| `2.0–2.4` | physically demanding work or very active leisure/competitive sport |

For regular strenuous sport or comparable leisure activity of about 30–60 minutes on 4–5 days per week, DGE permits adding `0.3` PAL units to the otherwise applicable base value.

MVP rules:

1. for age `< 1`, PAL is not required and is not used by the infant energy rule;
2. for age `>= 1`, a final resolved numeric PAL is required;
3. an unadjusted PAL must lie within the DGE-supported `1.2–2.4` range;
4. when the documented `+0.3` strenuous-activity adjustment is applied to a supported base PAL, the resulting final PAL may be as high as `2.7`;
5. derivation provenance retains the final PAL and whether the `+0.3` adjustment was applied;
6. `mvp-v1` does not automatically choose a midpoint from a descriptive PAL range — resolving the exact numeric PAL is profile input/preparation, not an implicit formula;
7. a PAL outside these source-supported rules makes energy derivation inapplicable rather than being silently clamped.

## Energy derivation

Variables:

- `A` — chronological age in years derived from date of birth at derivation time;
- `W` — current body weight in kg applicable to the derivation;
- `H` — height in metres;
- `PAL` — resolved physical-activity multiplier where required.

### Infants: age < 1 year

Use the DGE age/sex energy guiding value selected by the applicable infant age band. The active DGE reference derives infant energy independently of PAL.

### Children and adolescents: 1 <= age < 19 years

Use the Henry (2005) weight-and-height REE equation selected by sex and formula age band. To avoid propagating a known erroneous kcal transcription for the boys 3–10 equation, `mvp-v1` treats the published MJ/day coefficients as canonical and converts units only after evaluating the equation.

REE in MJ/day:

| Formula age band | Male | Female |
|---|---|---|
| `0–<3` | `0.118 × W + 3.59 × H - 1.55` | `0.127 × W + 2.94 × H - 1.20` |
| `3–<10` | `0.0632 × W + 1.31 × H + 1.28` | `0.0666 × W + 0.878 × H + 1.46` |
| `10–18` | `0.0651 × W + 1.11 × H + 1.25` | `0.0393 × W + 1.04 × H + 1.93` |

The member-level maintenance estimate includes growth energy according to the DGE derivation:

`maintenance_energy = REE × PAL × 1.01`.

The `0–<3` formula remains part of the source equation set, but the MVP uses the DGE infant guiding value for members under 1 year; therefore this equation is applied only from age 1 within this product. The source `10–18` formula is used for the product's `10 <= age < 19` adolescent band.

### Adults: age >= 19 years

DGE resting-energy expenditure in kcal/day:

- female: `REE = (0.047 × W - 0.01452 × A + 3.21) × 239`;
- male: `REE = (0.047 × W + 1.009 - 0.01452 × A + 3.21) × 239`.

Maintenance estimate:

`maintenance_energy = REE × PAL`.

The result is an estimate/guideline for planning, not a measured metabolic requirement.

## Weight-goal energy policy

Inputs:

- current weight and its observation date;
- target weight;
- target date;
- date of birth, sex, height and resolved physical activity required by the accepted adult model.

Rules:

1. `current_weight_date` must not be later than `derivation_date`;
2. the current observed weight is used as the planning baseline at `derivation_date`; `mvp-v1` does not extrapolate a different current weight from observation age, and the observation date remains provenance;
3. if target weight is absent, equal to current weight, or target date is absent, final energy target equals the maintenance estimate;
4. target date must be later than the derivation date for an active weight-change goal;
5. for age `>= 19`, use the NIDDK/Hall dynamic body-weight model identified by this standard set to derive the energy intake associated with the requested target weight and horizon beginning at `derivation_date`;
6. do not substitute the static `7700 kcal/kg` / `3500 kcal/lb` rule for the accepted model;
7. for age `< 19`, target weight/date do not alter energy in `mvp-v1`; the derivation records the weight goal as unsupported for automatic energy adjustment;
8. if the accepted adult model cannot produce an applicable result for the supplied profile/goal, the weight-goal component fails explicitly; it is not silently clamped or replaced by another formula.

The final energy target is the energy basis used by energy-relative nutrient references.

## Nutrient-target derivation

Resolve each applicable DGE/ÖGE reference in its source-native basis, then normalize it for the member.

### Absolute daily reference

`daily_target = source_amount_per_day`.

### Body-weight-relative reference

`daily_target = source_amount_per_kg_per_day × applicable_weight_kg`.

`applicable_weight_kg` is selected according to the source's own weight-basis rule; current body weight is not assumed universally. If the source applicability rule does not support the member state, derivation must expose that fact rather than inventing a weight basis.

### Percent-of-energy reference

For a nutrient with energy factor `F kcal/g` and source fraction `p`:

`daily_target_g = final_energy_target_kcal × p / F`.

For an interval `[p_min, p_max]`, apply the formula independently to both bounds. Energy factors are source data and must be retained with the standard set rather than duplicated inside Purchase Planning.

### Energy-density reference

For a reference expressed per 1000 kcal:

`daily_target = source_amount_per_1000_kcal × final_energy_target_kcal / 1000`.

### Thirty-day period

For the fixed MVP Calculation Period:

`period_target = daily_target × 30`.

For a source interval, both bounds are scaled by 30. A source point remains a point; the optimizer may define scoring tolerance downstream, but Nutrition Targeting does not invent one.

## Safety-limit derivation

An EFSA UL is a chronic **daily** intake limit. It therefore remains a daily Safety Limit in Member Nutrition Target provenance rather than being redefined as a 30-day safety budget.

Where a limit is applicable and the tracked nutrient identity/form matches the limit's scope, Purchase Planning may derive a 30-day comparison equivalent:

`period_equivalent = applicable_daily_limit × 30`.

This equivalent exists only to compare a 30-day **planned utilized** nutrient quantity with the daily reference basis. It is not an assertion that consumption on every day stays below the UL and is not a member-level safety guarantee.

The source limit kind and applicability remain attached to the result.

If Food Knowledge cannot represent the EFSA limit's substance/form at equal or finer semantic specificity, the limit remains diagnostic provenance and is not promoted to an enforceable product constraint, per [`ADR-004`](../decisions/ADR-004-canonical-nutrient-semantics.md).

## Household aggregation

Adequacy/reference demand aggregates additively by nutrient when the member target quantities have compatible semantics and units.

Member safety limits remain member-level evidence. The MVP may expose aggregate safety information for diagnostics, but a sum of member ULs is not a proof of individual safety because ADR-002 explicitly does not prove food allocation among members.

## Provenance required in a derived target

A rebuildable Member Nutrition Target identifies at least:

- `Nutrition Standard Set = mvp-v1`;
- derivation date;
- profile inputs used, including date of birth and current-weight observation date;
- resolved chronological age and source age band;
- resolved final PAL and strenuous-activity adjustment provenance when applicable;
- selected energy formula/policy;
- selected nutrient-reference identities and source semantic kinds;
- selected safety-limit identities when applicable;
- whether a weight goal was applied, ignored as non-active, unsupported, or inapplicable under the active policy.
